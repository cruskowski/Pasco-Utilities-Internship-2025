#!/usr/bin/env python3
"""
OCR Tool for PDF Files
This script extracts text from PDF files using Optical Character Recognition (OCR)
Uses EasyOCR for text extraction
"""

import os
import sys
from pdf2image import convert_from_path
import easyocr
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import cv2

def preprocess_image_for_ocr(image):
    """
    Preprocess image to enhance OCR accuracy
    """
    # Convert PIL to numpy array
    img_array = np.array(image)
    
    # Convert to grayscale if it's colored
    if len(img_array.shape) == 3:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_array
    
    # Apply noise reduction
    denoised = cv2.medianBlur(gray, 3)
    
    # Enhance contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(denoised)
    
    # Apply bilateral filter to reduce noise while keeping edges sharp
    filtered = cv2.bilateralFilter(enhanced, 9, 75, 75)
    
    # Apply threshold to get better contrast
    _, thresh = cv2.threshold(filtered, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return thresh

def create_layout_preserving_text(results, image_width, image_height, confidence_threshold=0.3):
    """
    Create text layout that preserves spatial positioning using a grid approach
    """
    # Filter results by confidence (lowered threshold to catch more text)
    filtered_results = [(bbox, text, conf) for bbox, text, conf in results if conf > confidence_threshold]
    
    if not filtered_results:
        return ""
    
    # Create a character grid to represent the page (increased resolution)
    grid_width = 150  # Characters per line (increased)
    grid_height = 80  # Lines per page (increased)
    
    char_grid = [[' ' for _ in range(grid_width)] for _ in range(grid_height)]
    
    # Calculate scaling factors
    x_scale = grid_width / image_width
    y_scale = grid_height / image_height
    
    for bbox, text, confidence in filtered_results:
        # Get bounding box coordinates
        top_left = bbox[0]
        bottom_right = bbox[2]
        
        # Convert to grid coordinates
        grid_x = int(top_left[0] * x_scale)
        grid_y = int(top_left[1] * y_scale)
        
        # Ensure coordinates are within bounds
        grid_x = max(0, min(grid_x, grid_width - len(text)))
        grid_y = max(0, min(grid_y, grid_height - 1))
        
        # Place text in grid
        for i, char in enumerate(text):
            if grid_x + i < grid_width:
                char_grid[grid_y][grid_x + i] = char
    
    # Convert grid back to text
    result_text = ""
    for row in char_grid:
        line = ''.join(row).rstrip()
        if line.strip():  # Only add non-empty lines
            result_text += line + "\n"
    
    return result_text

def extract_key_fields(results, image_width, image_height):
    """
    Extract specific key fields that are always in the same location
    """
    key_fields = {
        'PROJECT': '',
        'PCU_PROJECT_NO': '',
        'PROJECT_LOCATION': '',
        'NAME_OF_DEVELOPER': ''
    }
    
    # Define very precise regions based on the actual text locations
    regions = {
        'PROJECT': {
            'x_min': 0.25, 'x_max': 0.90,  # "Curley Road Outparcels Ltilities"
            'y_min': 0.063, 'y_max': 0.080   
        },
        'PCU_PROJECT_NO': {
            'x_min': 0.50, 'x_max': 0.80,  # "PCL #23-1015A1" 
            'y_min': 0.080, 'y_max': 0.105   
        },
        'PROJECT_LOCATION': {
            'x_min': 0.50, 'x_max': 0.85,  # "Eastafus_ 4l"
            'y_min': 0.105, 'y_max': 0.140   
        },
        'NAME_OF_DEVELOPER': {
            'x_min': 0.05, 'x_max': 0.40,  # "Meadow Ridge Owner_LLC"
            'y_min': 0.140, 'y_max': 0.175   
        }
    }
    
    # Extract text from each region
    for field_name, region in regions.items():
        field_text = []
        
        for bbox, text, confidence in results:
            if confidence > 0.2:  # Even lower confidence to catch more text
                # Get normalized coordinates (center of bounding box)
                x_center = (bbox[0][0] + bbox[2][0]) / 2 / image_width
                y_center = (bbox[0][1] + bbox[2][1]) / 2 / image_height
                
                # Check if text falls within the region
                if (region['x_min'] <= x_center <= region['x_max'] and 
                    region['y_min'] <= y_center <= region['y_max']):
                    # Skip obvious labels
                    if text.strip() not in ['PROJECT:', 'PCU', 'PROJECT', 'NO::', 'LOCATION:', 'PCU PROJECT NO::', 'PROJECT LOCATION:', '(Name', 'of', 'Developer)']:
                        field_text.append((bbox[0][0], text))  # Store with x-coordinate for sorting
        
        # Sort by x-coordinate and combine text
        field_text.sort(key=lambda x: x[0])
        key_fields[field_name] = ' '.join([text for _, text in field_text]).strip()
    
    # Clean up and format the extracted fields
    for field_name in key_fields:
        text = key_fields[field_name]
        # Remove extra spaces and clean up
        text = ' '.join(text.split())
        # Remove obvious form field labels that might be captured
        text = text.replace('PROJECT:', '')
        text = text.replace('PCU PROJECT NO::', '')
        text = text.replace('PROJECT LOCATION:', '')
        text = text.replace('LOCATLOCATION:', '')
        text = text.replace('(Name of Developer)', '')
        text = text.replace('(Grantor)', '')
        text = text.replace(',', '')
        key_fields[field_name] = text.strip()
    
    return key_fields

def extract_text_from_pdf(pdf_path, output_file=None, preserve_layout=True):
    """
    Extract text from PDF using EasyOCR
    
    Args:
        pdf_path (str): Path to the PDF file
        output_file (str, optional): Path to save extracted text
        preserve_layout (bool): Whether to preserve spatial layout of text
    
    Returns:
        str: Extracted text from the PDF
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    print(f"Processing PDF: {pdf_path}")
    print("Initializing EasyOCR reader...")
    
    # Initialize EasyOCR reader (this will download models on first use)
    reader = easyocr.Reader(['en'], gpu=False)
    
    print("Converting PDF pages to images...")
    
    try:
        # Convert PDF pages to images with higher DPI for better quality
        pages = convert_from_path(pdf_path, dpi=400)  # Increased from 300
        
        extracted_text = ""
        total_pages = len(pages)
        
        print(f"Found {total_pages} page(s). Starting OCR processing...")
        
        for page_num, page in enumerate(pages, 1):
            print(f"Processing page {page_num}/{total_pages}...")
            
            # Convert PIL image to numpy array for EasyOCR
            image_array = np.array(page)
            image_height, image_width = image_array.shape[:2]
            
            # Preprocess image for better OCR
            processed_image = preprocess_image_for_ocr(page)
            
            # Extract text using EasyOCR with multiple approaches
            results = reader.readtext(image_array, detail=1, paragraph=False)
            
            # Also try with the preprocessed image for better number detection
            results_processed = reader.readtext(processed_image, detail=1, paragraph=False)
            
            # Combine results from both approaches
            all_results = results + results_processed
            
            # Remove duplicates based on bounding box proximity
            unique_results = []
            for bbox, text, conf in all_results:
                is_duplicate = False
                for existing_bbox, existing_text, existing_conf in unique_results:
                    # Check if bounding boxes are close (within 10 pixels)
                    if (abs(bbox[0][0] - existing_bbox[0][0]) < 10 and 
                        abs(bbox[0][1] - existing_bbox[0][1]) < 10):
                        # Keep the one with higher confidence
                        if conf > existing_conf:
                            unique_results.remove((existing_bbox, existing_text, existing_conf))
                            unique_results.append((bbox, text, conf))
                        is_duplicate = True
                        break
                if not is_duplicate:
                    unique_results.append((bbox, text, conf))
            
            # Extract key fields for page 1 (main form)
            if page_num == 1:
                key_fields = extract_key_fields(unique_results, image_width, image_height)
                print("\n" + "="*60)
                print("EXTRACTED KEY FIELDS:")
                print("="*60)
                print(f"PROJECT:            {key_fields['PROJECT']}")
                print(f"PCU PROJECT NO:     {key_fields['PCU_PROJECT_NO']}")
                print(f"PROJECT LOCATION:   {key_fields['PROJECT_LOCATION']}")
                print(f"NAME OF DEVELOPER:  {key_fields['NAME_OF_DEVELOPER']}")
                print("="*60)
            
            # Add page separator
            extracted_text += f"\n--- Page {page_num} ---\n"
            
            if preserve_layout:
                # Use grid-based layout preservation
                page_text = create_layout_preserving_text(unique_results, image_width, image_height)
                extracted_text += page_text
            else:
                # Use line-based approach (previous method)
                # Sort results by vertical position (top to bottom), then horizontal (left to right)
                sorted_results = sorted(unique_results, key=lambda x: (x[0][0][1], x[0][0][0]))
                
                # Group text by approximate lines based on Y-coordinates
                lines = []
                current_line = []
                current_y = None
                y_tolerance = 20  # Pixels tolerance for same line
                
                for (bbox, text, confidence) in sorted_results:
                    if confidence > 0.3:  # Lowered confidence threshold
                        # Get the top-left Y coordinate
                        y_coord = bbox[0][1]
                        
                        if current_y is None or abs(y_coord - current_y) <= y_tolerance:
                            # Same line or first text
                            current_line.append((bbox[0][0], text))  # (x_coord, text)
                            current_y = y_coord if current_y is None else current_y
                        else:
                            # New line
                            if current_line:
                                # Sort current line by X coordinate (left to right)
                                current_line.sort(key=lambda x: x[0])
                                lines.append(current_line)
                            current_line = [(bbox[0][0], text)]
                            current_y = y_coord
                
                # Don't forget the last line
                if current_line:
                    current_line.sort(key=lambda x: x[0])
                    lines.append(current_line)
                
                # Reconstruct text with approximate spacing
                page_text = ""
                for line in lines:
                    line_text = ""
                    last_x = 0
                    
                    for x_coord, text in line:
                        # Add spaces based on horizontal distance
                        if last_x > 0:
                            x_diff = x_coord - last_x
                            # Add spaces proportional to distance (rough approximation)
                            spaces = max(1, int(x_diff / 25))  # Reduced divisor for more spacing
                            line_text += " " * spaces
                        
                        line_text += text
                        last_x = x_coord + len(text) * 8  # Reduced text width estimation
                    
                    page_text += line_text.rstrip() + "\n"
                
                extracted_text += page_text
            
            extracted_text += "="*50 + "\n"
        
        # Save to file if output path is provided
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                # Write key fields at the top if we extracted them
                if 'key_fields' in locals():
                    f.write("="*60 + "\n")
                    f.write("EXTRACTED KEY FIELDS:\n")
                    f.write("="*60 + "\n")
                    f.write(f"PROJECT:            {key_fields['PROJECT']}\n")
                    f.write(f"PCU PROJECT NO:     {key_fields['PCU_PROJECT_NO']}\n")
                    f.write(f"PROJECT LOCATION:   {key_fields['PROJECT_LOCATION']}\n")
                    f.write(f"NAME OF DEVELOPER:  {key_fields['NAME_OF_DEVELOPER']}\n")
                    f.write("="*60 + "\n\n")
                
                f.write(extracted_text)
            print(f"Text saved to: {output_file}")
        
        return extracted_text
        
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return None

def main():
    """
    Main function to run the OCR tool
    """
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Look for PDF files in the current directory
    pdf_files = [f for f in os.listdir(script_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("No PDF files found in the current directory.")
        return
    
    # If there's a specific PDF file named "Bill of Sale.pdf", use it
    pdf_file = "Bill of Sale.pdf"
    pdf_path = os.path.join(script_dir, pdf_file)
    
    if not os.path.exists(pdf_path):
        # If "Bill of Sale.pdf" doesn't exist, use the first PDF found
        pdf_file = pdf_files[0]
        pdf_path = os.path.join(script_dir, pdf_file)
    
    print(f"Found PDF file: {pdf_file}")
    
    # Ask user for layout preference
    print("\nLayout options:")
    print("1. Preserve spatial layout (grid-based) - maintains positioning")
    print("2. Line-based layout (reading order) - better for paragraphs")
    
    try:
        choice = input("Choose layout method (1 or 2, default=1): ").strip()
        preserve_layout = choice != "2"
    except (EOFError, KeyboardInterrupt):
        preserve_layout = True
        print("Using default: spatial layout preservation")
    
    # Output file for extracted text
    layout_suffix = "_spatial" if preserve_layout else "_linear"
    output_file = os.path.join(script_dir, f"{os.path.splitext(pdf_file)[0]}_extracted_text{layout_suffix}.txt")
    
    try:
        # Extract text from PDF
        extracted_text = extract_text_from_pdf(pdf_path, output_file, preserve_layout)
        
        if extracted_text:
            print("\n" + "="*60)
            print("EXTRACTED TEXT:")
            print("="*60)
            print(extracted_text)
            print("\n" + "="*60)
            print(f"Text extraction completed successfully!")
            print(f"Full text saved to: {output_file}")
        else:
            print("Failed to extract text from PDF.")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

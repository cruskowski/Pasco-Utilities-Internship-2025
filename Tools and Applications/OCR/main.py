import os
import sys
from pathlib import Path
import fitz  # PyMuPDF
import easyocr
import pytesseract
from pdf2image import convert_from_path
import cv2
import numpy as np
from PIL import Image
import argparse


class PDFOCRTool:
    """
    A comprehensive OCR tool for extracting text from PDF files.
    Supports multiple OCR engines: PyMuPDF (direct), EasyOCR, and Tesseract.
    """
    
    def __init__(self):
        self.easyocr_reader = None
        self.supported_formats = ['.pdf']
    
    def extract_text_pymupdf(self, pdf_path):
        """
        Extract text directly from PDF using PyMuPDF (fastest method).
        Works well for PDFs with selectable text.
        """
        try:
            doc = fitz.open(pdf_path)
            text_content = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                if text.strip():  # Only add non-empty pages
                    text_content.append(f"--- Page {page_num + 1} ---\n{text}\n")
            
            doc.close()
            return "\n".join(text_content)
        except Exception as e:
            print(f"Error with PyMuPDF extraction: {e}")
            return None
    
    def extract_text_easyocr(self, pdf_path, languages=['en']):
        """
        Extract text using EasyOCR (good for scanned documents).
        Converts PDF to images first, then applies OCR.
        """
        try:
            if self.easyocr_reader is None:
                print("Initializing EasyOCR...")
                self.easyocr_reader = easyocr.Reader(languages)
            
            # Convert PDF to images
            print("Converting PDF to images...")
            pages = convert_from_path(pdf_path, dpi=300)
            
            text_content = []
            for i, page in enumerate(pages):
                print(f"Processing page {i + 1}/{len(pages)} with EasyOCR...")
                
                # Convert PIL image to numpy array
                img_array = np.array(page)
                
                # Extract text
                results = self.easyocr_reader.readtext(img_array)
                
                page_text = []
                for (bbox, text, confidence) in results:
                    if confidence > 0.5:  # Filter low confidence results
                        page_text.append(text)
                
                if page_text:
                    text_content.append(f"--- Page {i + 1} ---\n" + "\n".join(page_text) + "\n")
            
            return "\n".join(text_content)
        except Exception as e:
            print(f"Error with EasyOCR extraction: {e}")
            return None
    
    def extract_text_tesseract(self, pdf_path, languages='eng'):
        """
        Extract text using Tesseract OCR (alternative OCR engine).
        Converts PDF to images first, then applies OCR.
        """
        try:
            # Convert PDF to images
            print("Converting PDF to images...")
            pages = convert_from_path(pdf_path, dpi=300)
            
            text_content = []
            for i, page in enumerate(pages):
                print(f"Processing page {i + 1}/{len(pages)} with Tesseract...")
                
                # Preprocess image for better OCR
                img_array = np.array(page)
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                
                # Apply threshold to get image with only black and white
                _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                
                # Convert back to PIL Image
                processed_img = Image.fromarray(thresh)
                
                # Extract text
                text = pytesseract.image_to_string(processed_img, lang=languages)
                
                if text.strip():
                    text_content.append(f"--- Page {i + 1} ---\n{text}\n")
            
            return "\n".join(text_content)
        except Exception as e:
            print(f"Error with Tesseract extraction: {e}")
            return None
    
    def extract_text(self, pdf_path, method='auto', languages=['en']):
        """
        Extract text from PDF using the specified method.
        
        Args:
            pdf_path (str): Path to the PDF file
            method (str): 'auto', 'pymupdf', 'easyocr', or 'tesseract'
            languages (list): Languages for OCR (EasyOCR format)
        
        Returns:
            str: Extracted text content
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        print(f"Processing: {os.path.basename(pdf_path)}")
        print(f"Method: {method}")
        
        if method == 'auto':
            # Try PyMuPDF first (fastest)
            print("\nTrying PyMuPDF (direct text extraction)...")
            text = self.extract_text_pymupdf(pdf_path)
            
            # If PyMuPDF returns empty or very little text, try OCR
            if not text or len(text.strip()) < 50:
                print("Direct text extraction returned minimal content. Trying OCR...")
                text = self.extract_text_easyocr(pdf_path, languages)
            
            return text
        
        elif method == 'pymupdf':
            return self.extract_text_pymupdf(pdf_path)
        
        elif method == 'easyocr':
            return self.extract_text_easyocr(pdf_path, languages)
        
        elif method == 'tesseract':
            tesseract_lang = 'eng' if 'en' in languages else languages[0]
            return self.extract_text_tesseract(pdf_path, tesseract_lang)
        
        else:
            raise ValueError("Method must be 'auto', 'pymupdf', 'easyocr', or 'tesseract'")
    
    def save_text_to_file(self, text, output_path):
        """Save extracted text to a file."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"Text saved to: {output_path}")
        except Exception as e:
            print(f"Error saving text: {e}")


def main():
    """Main function to run the OCR tool."""
    parser = argparse.ArgumentParser(description='Extract text from PDF files using OCR')
    parser.add_argument('pdf_path', nargs='?', help='Path to the PDF file')
    parser.add_argument('--method', choices=['auto', 'pymupdf', 'easyocr', 'tesseract'], 
                       default='auto', help='OCR method to use (default: auto)')
    parser.add_argument('--output', '-o', help='Output file path (optional)')
    parser.add_argument('--languages', nargs='+', default=['en'], 
                       help='Languages for OCR (default: en)')
    
    args = parser.parse_args()
    
    # If no PDF path provided, look for PDF files in current directory
    if not args.pdf_path:
        pdf_files = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
        if pdf_files:
            if len(pdf_files) == 1:
                args.pdf_path = pdf_files[0]
                print(f"Found PDF file: {args.pdf_path}")
            else:
                print("Multiple PDF files found:")
                for i, pdf_file in enumerate(pdf_files, 1):
                    print(f"{i}. {pdf_file}")
                
                try:
                    choice = int(input("Select a PDF file (enter number): ")) - 1
                    args.pdf_path = pdf_files[choice]
                except (ValueError, IndexError):
                    print("Invalid selection.")
                    return
        else:
            print("No PDF files found in current directory.")
            print("Usage: python main.py <pdf_path>")
            return
    
    # Initialize OCR tool
    ocr_tool = PDFOCRTool()
    
    try:
        # Extract text
        extracted_text = ocr_tool.extract_text(args.pdf_path, args.method, args.languages)
        
        if extracted_text:
            print("\n" + "="*60)
            print("EXTRACTED TEXT:")
            print("="*60)
            print(extracted_text)
            
            # Save to file if requested
            if args.output:
                ocr_tool.save_text_to_file(extracted_text, args.output)
            else:
                # Auto-generate output filename
                pdf_name = Path(args.pdf_path).stem
                output_path = f"{pdf_name}_extracted_text.txt"
                ocr_tool.save_text_to_file(extracted_text, output_path)
            
        else:
            print("No text could be extracted from the PDF.")
    
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()


import csv

def combine_large_csvs_robust(file1_path, file2_path, output_path):
    
    print("Starting to combine CSV files")
    
    with open(output_path, 'w', newline='', encoding='utf-8') as output_file:
        writer = None
        header_written = False
        
        # Process first file
        print("Processing first file...")
        #try:
        with open(file1_path, 'r', encoding='utf-8') as file1:
            reader = csv.reader(file1)
                
            for row_num, row in enumerate(reader):
                if row_num == 0:  # Header row
                    writer = csv.writer(output_file)
                    writer.writerow(row)
                    header_written = True
                    print("Header written from first file")
                else:
                    writer.writerow(row)
                    
                if row_num % 10000 == 0:  # Progress indicator
                    print(f"Processed {row_num} rows from file 1...")
                        
        """except UnicodeDecodeError:
            with open(file1_path, 'r', encoding='latin-1') as file1:
                reader = csv.reader(file1)
                
                for row_num, row in enumerate(reader):
                    if row_num == 0:  # Header row
                        writer = csv.writer(output_file)
                        writer.writerow(row)
                        header_written = True
                        print("Header written from first file")
                    else:
                        writer.writerow(row)
                    
                    if row_num % 10000 == 0:  # Progress indicator
                        print(f"Processed {row_num} rows from file 1...")
                        """
        
        print("First file completed!")
        
        # Process second file
        print("Processing second file...")
        #try:
        with open(file2_path, 'r', encoding='utf-8') as file2:
            reader = csv.reader(file2)
                
            for row_num, row in enumerate(reader):
                if row_num == 0:  # Skip header row for second file
                    print("Skipping header from second file")
                    continue
                else:
                    writer.writerow(row)
                    
                if row_num % 10000 == 0:  # Progress indicator
                    print(f"Processed {row_num} rows from file 2...")
                        
        """except UnicodeDecodeError:
            with open(file2_path, 'r', encoding='latin-1') as file2:
                reader = csv.reader(file2)
                
                for row_num, row in enumerate(reader):
                    if row_num == 0:  # Skip header row for second file
                        print("Skipping header from second file")
                        continue
                    else:
                        writer.writerow(row)
                    
                    if row_num % 10000 == 0:  # Progress indicator
                        print(f"Processed {row_num} rows from file 2...")
        """
        print("Second file completed!")
    
    print("Files successfully combined")
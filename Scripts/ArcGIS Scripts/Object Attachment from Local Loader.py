import arcpy
import os
import csv
from datetime import datetime


feature_service_url = "https://pascogis.pascocountyfl.net/giswebu/rest/services/Engineering/PascoCo_Utilities_Developments/FeatureServer/0"
#folder with zipped files path
zip_folder = r"U:\UTIL_ENG\zChristopher\ARCGIS MAX\zipped all"
#field/column containing the PCU numbers to match
pcu_field = "PCU_NUM"

# Create CSV file for logging (save to zip folder directory)
csv_filename = f"attachment_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
csv_path = os.path.join(zip_folder, csv_filename)

# Create match table for AddAttachments (temp CSV)
match_table_path = os.path.join(zip_folder, f"temp_match_table_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

# Initialize CSV file with headers
with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['PCU_Number', 'Zip_Filename', 'Object_ID', 'Status', 'Reason', 'File_Size_MB', 'Timestamp'])

# Create match table for AddAttachments
with open(match_table_path, 'w', newline='', encoding='utf-8') as match_file:
    match_writer = csv.writer(match_file)
    match_writer.writerow(['OBJECTID', 'PATH'])

# Create a cursor to iterate through features
successful_attachments = []
with arcpy.da.SearchCursor(feature_service_url, ["OID@", pcu_field]) as cursor:
    for row in cursor:
        oid = row[0]
        pcu_num = row[1]
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if pcu_num:  # Check if PCU number is not None or empty
            # Look for corresponding zip file with exact PCU number match
            zip_filename = f"{pcu_num}.zip"
            zip_path = os.path.join(zip_folder, zip_filename)
            
            if os.path.exists(zip_path):
                try:
                    # Get file size in MB
                    file_size_bytes = os.path.getsize(zip_path)
                    file_size_mb = round(file_size_bytes / (1024 * 1024), 2)
                    
                    # Add to match table for batch processing
                    with open(match_table_path, 'a', newline='', encoding='utf-8') as match_file:
                        match_writer = csv.writer(match_file)
                        match_writer.writerow([oid, zip_path])
                    
                    # Store for success logging
                    successful_attachments.append([pcu_num, zip_filename, oid, file_size_mb, timestamp])
                    
                    print(f"Prepared {zip_filename} for feature with OID {oid} (PCU: {pcu_num}) - Size: {file_size_mb}MB")
                    
                except Exception as e:
                    # Log failure due to file access error
                    with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow([pcu_num, zip_filename, oid, 'FAILURE', f'File access error: {str(e)}', 'N/A', timestamp])
                    
                    print(f"Error accessing file for PCU {pcu_num}: {str(e)}")
            else:
                # Log failure due to missing file
                with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([pcu_num, zip_filename, oid, 'FAILURE', 'Zip file not found', 'N/A', timestamp])
                
                print(f"Zip file not found for PCU: {pcu_num}")
        else:
            # Log failure due to empty PCU number
            with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['N/A', 'N/A', oid, 'FAILURE', 'Empty PCU_NUM field', 'N/A', timestamp])
            
            print(f"Empty PCU_NUM for feature with OID {oid}")

# Process all attachments in batch
if successful_attachments:
    try:
        print("Processing attachments in batch...")
        arcpy.AddAttachments_management(
            feature_service_url,
            "OBJECTID",
            match_table_path,
            "OBJECTID",
            "PATH"
        )
        
        # Log all successes
        for attachment_info in successful_attachments:
            pcu_num, zip_filename, oid, file_size_mb, timestamp = attachment_info
            with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([pcu_num, zip_filename, oid, 'SUCCESS', 'Attachment added successfully', file_size_mb, timestamp])
        
        print(f"Successfully added {len(successful_attachments)} attachments!")
        
    except Exception as e:
        print(f"Batch attachment error: {str(e)}")
        # Log batch failure
        for attachment_info in successful_attachments:
            pcu_num, zip_filename, oid, file_size_mb, timestamp = attachment_info
            with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([pcu_num, zip_filename, oid, 'FAILURE', f'Batch attachment error: {str(e)}', file_size_mb, timestamp])

# Clean up temporary match table
try:
    os.remove(match_table_path)
    print("Temporary files cleaned up.")
except:
    print(f"Could not remove temporary file: {match_table_path}")

print(f"Attachment process completed! Log file created: {csv_path}")
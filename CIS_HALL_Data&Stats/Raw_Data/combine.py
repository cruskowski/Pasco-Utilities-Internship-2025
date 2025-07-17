import pandas as pd
import glob
import os

def combine_csv_files():
    """
    Combine all cycle data files into one CSV file.
    All files are pipe-delimited and have the same header structure.
    """
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Pattern to match all cycle files (excluding the combine.py script)
    pattern = os.path.join(script_dir, "*cycle*")
    
    # Get all matching files
    files = glob.glob(pattern)
    
    # Filter out any .py files just in case
    files = [f for f in files if not f.endswith('.py')]
    
    print(f"Found {len(files)} cycle files to combine:")
    for file in sorted(files):
        print(f"  - {os.path.basename(file)}")
    
    # List to store all dataframes
    all_dfs = []
    
    # Read each file and append to the list
    for file in files:
        try:
            print(f"\nReading: {os.path.basename(file)}")
            
            # Read the pipe-delimited file
            df = pd.read_csv(file, delimiter='|', dtype=str)
            
            # Add a column to track the source file
            df['SOURCE_FILE'] = os.path.basename(file)
            
            print(f"  - Rows: {len(df)}")
            print(f"  - Columns: {len(df.columns)}")
            
            all_dfs.append(df)
            
        except Exception as e:
            print(f"Error reading {file}: {e}")
    
    if not all_dfs:
        print("No files were successfully read!")
        return
    
    # Combine all dataframes
    print(f"\nCombining {len(all_dfs)} dataframes...")
    combined_df = pd.concat(all_dfs, ignore_index=True)
    
    print(f"Combined dataset:")
    print(f"  - Total rows: {len(combined_df)}")
    print(f"  - Total columns: {len(combined_df.columns)}")
    
    # Save to CSV file
    output_file = os.path.join(script_dir, "combined_cycles.csv")
    combined_df.to_csv(output_file, index=False)
    
    print(f"\nCombined data saved to: {output_file}")
    
    # Show summary by source file
    print(f"\nSummary by source file:")
    source_summary = combined_df['SOURCE_FILE'].value_counts().sort_index()
    for source, count in source_summary.items():
        print(f"  - {source}: {count} rows")
    
    return output_file

if __name__ == "__main__":
    combine_csv_files()
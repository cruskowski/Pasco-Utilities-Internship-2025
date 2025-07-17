import pandas as pd
import glob
import os

def combine_and_analyze_csv_files():
    """
    Combine all cycle data files and analyze low/high read limits by unique account ID.
    """
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Pattern to match all cycle files (excluding python files)
    pattern = os.path.join(script_dir, "*cycle*")
    
    # Get all matching files
    files = glob.glob(pattern)
    
    # Filter out any .py files and .csv files
    files = [f for f in files if not f.endswith('.py') and not f.endswith('.csv')]
    
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
    
    # Save combined data to CSV
    output_file = os.path.join(script_dir, "combined_cycles.csv")
    combined_df.to_csv(output_file, index=False)
    print(f"\nCombined data saved to: {output_file}")
    
    # Now analyze the data for unique account IDs
    print("\n" + "="*80)
    print("ANALYZING LOW AND HIGH READ LIMITS BY UNIQUE ACCOUNT ID")
    print("="*80)
    
    # Convert LOW_READ_LIMIT and HIGH_READ_LIMIT to numeric, handling empty/null values
    combined_df['LOW_READ_LIMIT_NUM'] = pd.to_numeric(combined_df['LOW_READ_LIMIT'], errors='coerce')
    combined_df['HIGH_READ_LIMIT_NUM'] = pd.to_numeric(combined_df['HIGH_READ_LIMIT'], errors='coerce')
    
    # Group by ACCOUNT_ID and calculate sums
    account_summary = combined_df.groupby('ACCOUNT_ID').agg({
        'LOW_READ_LIMIT_NUM': 'sum',
        'HIGH_READ_LIMIT_NUM': 'sum',
        'ACCOUNT_FULL_NAME': 'first',  # Get the name for reference
        'SOURCE_FILE': 'count'  # Count how many records per account
    }).round(2)
    
    # Rename columns for clarity
    account_summary.columns = ['SUM_LOW_READ_LIMIT', 'SUM_HIGH_READ_LIMIT', 'ACCOUNT_NAME', 'RECORD_COUNT']
    
    # Sort by account ID
    account_summary = account_summary.sort_index()
    
    print(f"\nSummary for {len(account_summary)} unique account IDs:")
    print(f"{'ACCOUNT_ID':<12} {'ACCOUNT_NAME':<40} {'RECORDS':<8} {'SUM_LOW_LIMIT':<15} {'SUM_HIGH_LIMIT':<15}")
    print("-" * 100)
    
    for account_id, row in account_summary.iterrows():
        account_name = str(row['ACCOUNT_NAME'])[:35] + "..." if len(str(row['ACCOUNT_NAME'])) > 35 else str(row['ACCOUNT_NAME'])
        print(f"{account_id:<12} {account_name:<40} {int(row['RECORD_COUNT']):<8} {row['SUM_LOW_READ_LIMIT']:<15} {row['SUM_HIGH_READ_LIMIT']:<15}")
    
    # Save the summary to a separate CSV
    summary_file = os.path.join(script_dir, "account_read_limits_summary.csv")
    account_summary.to_csv(summary_file)
    print(f"\nAccount summary saved to: {summary_file}")
    
    # Show overall statistics
    print(f"\nOVERALL STATISTICS:")
    print(f"  - Total unique accounts: {len(account_summary)}")
    print(f"  - Total sum of all low read limits: {account_summary['SUM_LOW_READ_LIMIT'].sum():,.2f}")
    print(f"  - Total sum of all high read limits: {account_summary['SUM_HIGH_READ_LIMIT'].sum():,.2f}")
    print(f"  - Average low read limit per account: {account_summary['SUM_LOW_READ_LIMIT'].mean():,.2f}")
    print(f"  - Average high read limit per account: {account_summary['SUM_HIGH_READ_LIMIT'].mean():,.2f}")
    
    # Show top 10 accounts by high read limit
    print(f"\nTOP 10 ACCOUNTS BY HIGH READ LIMIT:")
    top_10_high = account_summary.nlargest(10, 'SUM_HIGH_READ_LIMIT')
    print(f"{'ACCOUNT_ID':<12} {'ACCOUNT_NAME':<35} {'SUM_HIGH_LIMIT':<15}")
    print("-" * 70)
    for account_id, row in top_10_high.iterrows():
        account_name = str(row['ACCOUNT_NAME'])[:30] + "..." if len(str(row['ACCOUNT_NAME'])) > 30 else str(row['ACCOUNT_NAME'])
        print(f"{account_id:<12} {account_name:<35} {row['SUM_HIGH_READ_LIMIT']:<15}")
    
    return combined_df, account_summary

if __name__ == "__main__":
    combined_data, summary = combine_and_analyze_csv_files()

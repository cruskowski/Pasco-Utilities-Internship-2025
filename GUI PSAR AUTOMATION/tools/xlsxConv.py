from matplotlib.pylab import number
import pandas as pd

def convert_xlsx_to_csv(xlsx_file, csv_file):
    try:
        # Read the Excel file without treating first row as header
        df = pd.read_excel(xlsx_file, engine='openpyxl', header=None)
        
        # Save to CSV
        df.to_csv(csv_file, index=False, header=False)
        print(f"Successfully converted {xlsx_file} to {csv_file}")
        
        # Display information about the converted data
        print(f"\nData Preview:")
        print(f"Shape: {df.shape} (rows, columns)")
        print(f"\nFirst 10 rows:")
        print(df.head(10))
        print(f"\nLast 5 rows:")
        print(df.tail())
        
        # Check if this looks like SQL code
        first_cell = str(df.iloc[0, 0]) if not df.empty else ""
        if "sql" in first_cell.lower() or "select" in first_cell.lower() or "declare" in first_cell.lower():
            print(f"\nNote: This appears to contain SQL code rather than tabular data.")
            print(f"You may want to extract and clean the SQL queries separately.")

    except FileNotFoundError:
        print(f"Error: The file {xlsx_file} does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        print("\nConversion process completed.")
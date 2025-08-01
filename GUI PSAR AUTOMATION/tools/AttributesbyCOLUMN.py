import pandas as pd

def list_unique_zone_names(csv_file_path):
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file_path)
        
        # Check if ZONE NAME column exists
        if 'ZONE NAME' not in df.columns:
            print("Available columns in the dataset:")
            print(df.columns.tolist())
            
            # Look for similar column names
            zone_cols = [col for col in df.columns if 'ZONE' in col.upper()]
            if zone_cols:
                print(f"\nColumns containing 'ZONE': {zone_cols}")
                return None
            else:
                print("No 'ZONE NAME' column found in the dataset.")
                return None
        
        # Get unique values from ZONE NAME column
        unique_zones = df['ZONE NAME'].unique()
        
        # Remove NaN values if any and sort alphabetically
        unique_zones = [zone for zone in unique_zones if pd.notna(zone)]
        unique_zones.sort()
        
        print(f"Found {len(unique_zones)} unique zone names:")
        print("=" * 50)
        
        for i, zone in enumerate(unique_zones, 1):
            print(f"{i:2d}. {zone}")
        
        # Show count of records per zone (sorted alphabetically)
        print("\n" + "=" * 50)
        print("Record count per zone:")
        zone_counts = df['ZONE NAME'].value_counts()
        
        # Sort by zone name alphabetically
        for zone in unique_zones:
            count = zone_counts[zone]
            print(f"{zone}: {count:,} records")
        
        return unique_zones
        
    except FileNotFoundError:
        print(f"Error: File not found - {csv_file_path}")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

# Run the function
csv_file_path = r'C:\Users\cruskowski\Desktop\GUI PSAR AUTOMATION\Data_Pre\CSV Combined.csv'
unique_zones = list_unique_zone_names(csv_file_path)
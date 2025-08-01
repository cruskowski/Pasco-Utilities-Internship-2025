import pandas as pd
import os



def bulkMeterConsumptionFUNC(file3_path):
    # Check if file exists first
    """if not os.path.exists(file3_path):
        print(f"Error: File not found - {file3_path}")
        return 0
    
    try:
        bulkDF = pd.read_csv(file3_path, low_memory=False)
        bulktotal = bulkDF['BILLED METER CONSUMPTION'].sum()
        print(f"bulktotal: {bulktotal}")
        return bulktotal
    except Exception as e:
        print(f"Error reading file: {e}")
        return 0"""
    
    bulktotal = input("Enter the total billed meter consumption for the bulk data:, ex: 100100100 ")

    print(f"bulktotal: {bulktotal}")

    return float(bulktotal)
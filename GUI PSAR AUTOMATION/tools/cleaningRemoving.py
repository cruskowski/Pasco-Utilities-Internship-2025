import pandas as pd

def cleaningRemovingFUNC(output_path, file3_path):
    
    mainDF = pd.read_csv(output_path, low_memory=False)
    bulkDF = pd.read_csv(file3_path, low_memory=False)



    original_len = float(len(mainDF))
    # Remove rows where column ZONE NAME contains excluded locations (only if column exists)
    excluded_locations = ['BLANTON-NE', 'PINEBREEZE COURT-SE', 'JASMINE LAKES-NW']

    if 'ZONE NAME' in mainDF.columns:
        mainDF = mainDF[~mainDF['ZONE NAME'].isin(excluded_locations)]
        print(f"Removed excluded locations from mainDF")
    else:
        print("Warning: Column 'ZONE NAME' not found in mainDF - skipping location removal")

    if 'ZONE NAME' in bulkDF.columns:
        bulkDF = bulkDF[~bulkDF['ZONE NAME'].isin(excluded_locations)]
        print(f"Removed excluded locations from bulkDF")
    else:
        print("Warning: Column 'ZONE NAME' not found in bulkDF - skipping location removal")

    print(f"After removing excluded locations - mainDF: {len(mainDF):,}, bulkDF: {len(bulkDF):,}")
    print(f'removed {original_len - float(len(mainDF))} rows from mainDF')
    # Save cleaned data back to files
    mainDF.to_csv(output_path, index=False)
    bulkDF.to_csv(file3_path, index=False)
    
    print("Cleaned data saved successfully!")
    
    return mainDF, bulkDF

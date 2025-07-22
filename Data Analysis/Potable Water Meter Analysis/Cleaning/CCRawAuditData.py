import pandas as pd

# Read both CSV files
a = pd.read_csv(r'C:\Users\cruskowski\Desktop\GitHub Local Repository\Pasco-Utilities-Internship-2025\Data Analysis\Potable Water Meter Analysis\Data\pre_Audit 2024 Raw Data 2.csv', low_memory=False)
b = pd.read_csv(r'C:\Users\cruskowski\Desktop\GitHub Local Repository\Pasco-Utilities-Internship-2025\Data Analysis\Potable Water Meter Analysis\Data\pre_Audit 2024 Raw Data.csv', low_memory=False)

# Concatenate the DataFrames
combined = pd.concat([a, b], ignore_index=True)

# If there is a date column, sort by it (replace 'DATE_COLUMN_NAME' with the actual column name, e.g., 'BILL DATE')
combined['BILL DATE'] = pd.to_datetime(combined['BILL DATE'])
combined = combined.sort_values('BILL DATE')
#combined = combined.dropna()

# Save the merged and sorted DataFrame to a new CSV
combined.to_csv(r'C:\Users\cruskowski\Desktop\GitHub Local Repository\Pasco-Utilities-Internship-2025\Data Analysis\Potable Water Meter Analysis\Data\SECOND_Audit 2024 Raw Data Combined.csv', index=False)

print(combined.head())
print(combined.tail())
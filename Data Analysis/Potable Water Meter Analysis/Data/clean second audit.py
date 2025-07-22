import pandas as pd

df = pd.read_csv(r"C:\Users\cruskowski\Desktop\GitHub Local Repository\Pasco-Utilities-Internship-2025\Data Analysis\Potable Water Meter Analysis\Data\SECOND_Audit 2024 Raw Data Combined.csv")

print(f"Original data shape: {df.shape}")

# Filter to keep only rows where REVENUE CLASS DESCRIPTION is "SINGLE FAMILY"
filtered_df = df[df['REVENUE CLASS DESCRIPTION'] == 'SINGLE FAMILY MOBILE']

print(f"Filtered data shape: {filtered_df.shape}")
print(f"Rows removed: {df.shape[0] - filtered_df.shape[0]}")

# Save to new CSV file
output_file = r"C:\Users\cruskowski\Desktop\GitHub Local Repository\Pasco-Utilities-Internship-2025\Data Analysis\Potable Water Meter Analysis\Data\SECOND_Audit_2024_Single_FamilyMOBILE_Only.csv"
filtered_df.to_csv(output_file, index=False)

print(f"Filtered data saved to: {output_file}")





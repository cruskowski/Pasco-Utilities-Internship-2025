import pandas as pd
import matplotlib.pyplot as plt

# Load and clean data as before
df = pd.read_csv("fire hydrant eat maintnence.csv", skiprows=2)
df = df.dropna(how='all')
df.columns = [
    'Date Completed',
    'Description',
    'Problem Code',
    'Component Code',
    'Cause Code',
    'Action Code',
    'Labor Hours',
    'Labor Costs',
    'Parts Cost',
    'Vehicle Cost',
    'Total Cost'
]
df['Date Completed'] = pd.to_datetime(df['Date Completed'], errors='coerce')
for col in ['Labor Hours', 'Labor Costs', 'Parts Cost', 'Vehicle Cost', 'Total Cost']:
    df[col] = (
        df[col]
        .astype(str)
        .str.replace(',', '', regex=False)
        .str.strip()
        .replace('', '0')
        .astype(float)
    )

# Set date as index and sort
df = df.set_index('Date Completed').sort_index()

# Resample by month and sum total costs
monthly_costs = df['Total Cost'].resample('M').sum()

# Plot the time series
plt.figure(figsize=(10, 5))
monthly_costs.plot()
plt.title('Monthly Fire Hydrant Maintenance Costs')
plt.xlabel('Month')
plt.ylabel('Total Cost ($)')
plt.tight_layout()
plt.show()

# Optional: print summary statistics
print("Monthly Cost Summary Statistics:")
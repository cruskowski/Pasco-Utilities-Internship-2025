import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# Load data from a CSV file
data = pd.read_csv('data/wMainpotable.csv', low_memory=False)

# Replace '<Null>' strings with actual NaN values
data = data.replace('<Null>', pd.NA)

# Only keep essential columns and handle missing values more strategically
# Focus on key numeric and categorical columns that are most likely to have data
essential_columns = ['OBJECTID *', 'Length', 'Diameter', 'Material', 'System Type', 'Water Type', 'Operations Status', 'Map Number', 'Active Flag']
data = data[essential_columns]

# Drop rows only if they're missing critical data (Length or OBJECTID)
data = data.dropna(subset=['OBJECTID *', 'Length'])

# Fill remaining missing values with appropriate defaults
data['Material'] = data['Material'].fillna('Unknown')
data['System Type'] = data['System Type'].fillna('Unknown')
data['Water Type'] = data['Water Type'].fillna('Unknown')
data['Operations Status'] = data['Operations Status'].fillna('Unknown')
data['Active Flag'] = data['Active Flag'].fillna('TRUE')
data['Map Number'] = data['Map Number'].fillna(0)

# Clean the Diameter column (remove quotes and convert to numeric, handle errors)
data['Diameter'] = data['Diameter'].astype(str).str.replace('"', '').str.replace('""', '')
data['Diameter'] = pd.to_numeric(data['Diameter'], errors='coerce')
data['Diameter'] = data['Diameter'].fillna(data['Diameter'].median())

# Convert categorical variables to numerical variables
data['Material'] = pd.Categorical(data['Material']).codes
data['System Type'] = pd.Categorical(data['System Type']).codes
data['Water Type'] = pd.Categorical(data['Water Type']).codes
data['Operations Status'] = pd.Categorical(data['Operations Status']).codes
data['Active Flag'] = pd.Categorical(data['Active Flag']).codes

# Scale the data using StandardScaler
scaler = StandardScaler()
data[['Length', 'OBJECTID *', 'Map Number', 'Diameter', 'Material', 'System Type', 'Water Type', 'Operations Status', 'Active Flag']] = scaler.fit_transform(data[['Length', 'OBJECTID *', 'Map Number', 'Diameter', 'Material', 'System Type', 'Water Type', 'Operations Status', 'Active Flag']])

# Train an isolation forest model on the data
model = IsolationForest(n_estimators=100, contamination=0.1)
model.fit(data)

# Make predictions on the data
y_pred = model.predict(data)

# Get anomaly scores (more negative = more anomalous)
anomaly_scores = model.decision_function(data)

# Get anomalies (outliers) and sort by anomaly score
anomaly_mask = y_pred == -1
anomalies = data[anomaly_mask].copy()
anomaly_scores_filtered = anomaly_scores[anomaly_mask]

# Add anomaly scores to the anomalies dataframe and sort
anomalies['anomaly_score'] = anomaly_scores_filtered
anomalies = anomalies.sort_values('anomaly_score')  # Most anomalous (most negative) first

normal_points = data[y_pred == 1]

print(f"Total records: {len(data)}")
print(f"Normal records: {len(normal_points)}")
print(f"Anomaly records: {len(anomalies)}")
print(f"Anomaly percentage: {len(anomalies)/len(data)*100:.2f}%")
print("\n" + "="*50)
print("ANOMALIES DETECTED (sorted by anomaly score - most anomalous first):")
print("="*50)
print(anomalies[['OBJECTID *', 'Length', 'Diameter', 'Material', 'System Type', 'Map Number', 'anomaly_score']])

# To see the original values, let's reload and show original data for anomalies
print("\n" + "="*50)
print("ORIGINAL VALUES FOR ANOMALIES (sorted by anomaly score):")
print("="*50)

# Reload original data to show unscaled values
original_data = pd.read_csv('data/wMainpotable.csv', low_memory=False)
original_data = original_data.replace('<Null>', pd.NA)
original_data = original_data[essential_columns]
original_data = original_data.dropna(subset=['OBJECTID *', 'Length'])

# Show original values for the anomaly indices (sorted by anomaly score)
anomaly_indices = anomalies.index
original_anomalies = original_data.loc[anomaly_indices].copy()
original_anomalies['anomaly_score'] = anomalies['anomaly_score']
print(original_anomalies[['OBJECTID *', 'Length', 'Diameter', 'Material', 'System Type', 'Map Number', 'anomaly_score']])
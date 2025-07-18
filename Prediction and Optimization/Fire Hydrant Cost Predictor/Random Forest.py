import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np

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

# Feature engineering for Description (column 2)
for keyword in ['flowtest', 'repaired', 'inspect', 'replaced']:
    df[keyword.capitalize()] = df['Description'].str.contains(keyword, case=False, na=False).astype(int)

# Extract year and month from Date Completed (column 1)
df['Year'] = df['Date Completed'].dt.year
df['Month'] = df['Date Completed'].dt.month

# One-hot encode categorical columns: Problem Code (3), Component Code (4), Cause Code (5), Action Code (6)
categorical_cols = ['Problem Code', 'Component Code', 'Cause Code', 'Action Code']
df_encoded = pd.get_dummies(df[categorical_cols], drop_first=True)

# Combine all features
X = pd.concat([
    df[['Flowtest', 'Repaired', 'Inspect', 'Replaced', 'Year', 'Month']],
    df_encoded
], axis=1)
y = df['Labor Hours']

# Drop rows with missing values in X or y
mask = X.notnull().all(axis=1) & y.notnull()
X = X[mask]
y = y[mask]

# Train/test split and modeling with Random Forest
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

print("Random Forest Labor Hours Prediction (with columns 1-6):")
print("R^2:", r2_score(y_test, y_pred))
print("RMSE:")
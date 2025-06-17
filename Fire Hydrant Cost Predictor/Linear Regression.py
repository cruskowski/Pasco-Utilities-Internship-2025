import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

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

# Drop rows with missing target values
df = df.dropna(subset=['Labor Hours', 'Total Cost'])

# Encode categorical variables
df_encoded = pd.get_dummies(df[['Problem Code', 'Component Code', 'Cause Code', 'Action Code']], drop_first=True)

# Combine with numeric predictors
X = pd.concat([df_encoded, df[['Parts Cost', 'Vehicle Cost']]], axis=1)

# Predict Labor Hours
y_hours = df['Labor Hours']
X_train, X_test, y_train, y_test = train_test_split(X, y_hours, test_size=0.2, random_state=42)
model_hours = LinearRegression()
model_hours.fit(X_train, y_train)
y_pred_hours = model_hours.predict(X_test)
print("Labor Hours Prediction:")
print("R^2:", r2_score(y_test, y_pred_hours))
print("RMSE:", np.sqrt(mean_squared_error(y_test, y_pred_hours)))

# Predict Total Cost
y_cost = df['Total Cost']
X_train, X_test, y_train, y_test = train_test_split(X, y_cost, test_size=0.2, random_state=42)
model_cost = LinearRegression()
model_cost.fit(X_train, y_train)
y_pred_cost = model_cost.predict(X_test)
print("\nTotal Cost Prediction:")
print("R^2:", r2_score(y_test, y_pred_cost))
print("RMSE:", np.sqrt(mean_squared_error(y_test, y_pred_cost)))
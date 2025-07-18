import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

XTICKS_ROTATION = 45

def Linear_Regression(csv_path):
    """
    Performs linear regression to forecast meter installations by month.
    """
    # Load data
    df = pd.read_csv(csv_path, parse_dates=['Date'])
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    monthly_counts = df.groupby('Month').size().reset_index(name='Amount Installed')

    # Prepare data for regression
    monthly_counts['Month_Num'] = range(len(monthly_counts))
    X = monthly_counts[['Month_Num']]
    y = monthly_counts['Amount Installed']

    # Fit linear regression model
    model = LinearRegression()
    model.fit(X, y)

    # Predict values
    monthly_counts['Forecast'] = model.predict(X)

    # Plot actual vs forecast
    plt.figure(figsize=(14, 6))
    plt.plot(monthly_counts['Month'], y, label='Actual', marker='o')
    plt.plot(monthly_counts['Month'], monthly_counts['Forecast'], label='Forecast (Linear Regression)', linestyle='--')

    N = max(1, len(monthly_counts) // 12)
    plt.xticks(
        ticks=range(0, len(monthly_counts), N),
        labels=monthly_counts['Month'][::N],
        rotation=XTICKS_ROTATION
    )
    plt.xlabel('Month')
    plt.ylabel('Amount Installed')
    plt.title('Linear Regression Forecast of Meter Installations')
    plt.tight_layout()
    plt.show()

    return model

# Example usage:
# forecast_installations(r"C:\Users\cruskowski\Desktop\Local Repository\Potable Water Meter
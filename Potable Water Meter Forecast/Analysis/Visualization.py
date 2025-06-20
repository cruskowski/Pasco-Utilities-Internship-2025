import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

XTICKS_ROTATION = 45  # Rotation angle for x-axis tick labels

def visualize_installed_by_month(file_path): # Function to visualize the number of meters installed by month , file_path is used when the function is called in main.py
    df = pd.read_csv(file_path, parse_dates=['Date'])#parse dates=['Date'] ensures that the 'Date' column is parsed as datetime objects

    # Create a 'Month' column (year and month)
    df['Month'] = df['Date'].dt.to_period('M').astype(str) #extracts the year and month from each entry in the date column, .dt.to_period('M') part converts each date to a "period" representing just the year and month, The .astype(str) then converts these period objects into string format, making them easier to use as labels or for grouping in later analysis. This transformation is useful for summarizing or visualizing data on a monthly basis rather than by individual dates.

    # Count installations per month
    monthly_counts = df.groupby('Month').size().reset_index(name='Amount Installed') # groups the data by values in the month column, splits data into groups where each group contain all rows from the same month size() counts the number of rows in each group giving the number of installations per month, reset_index(name='Amount Installed') resets the index of the resulting DataFrame and renames the count column to 'Amount Installed'.

    # Plot
    plt.figure(figsize=(14, 6)) #14 inches by 6 inches
    sns.barplot(data=monthly_counts, x='Month', y='Amount Installed', color='skyblue', edgecolor='black')

    # Show only every Nth month label to avoid crowding
    N = max(1, len(monthly_counts) // 12)  # Show about 12 labels max
    plt.xticks(
        ticks=range(0, len(monthly_counts), N),
        labels=monthly_counts['Month'][::N],
        rotation=XTICKS_ROTATION
    )

    plt.xlabel('Month')
    plt.ylabel('Amount Installed')
    plt.title('Number of Meters Installed by Month')
    plt.tight_layout()
    plt.show()

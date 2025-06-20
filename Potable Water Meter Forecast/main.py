from Analysis.Visualization import visualize_installed_by_month #package from analysis folder so we can use it
from Forecasting.LinearRRegression import Linear_Regression 

if __name__ == "__main__":
    visualize_installed_by_month(r"C:\Users\cruskowski\Desktop\Local Repository\Potable Water Meter Forecast\Data\Installed Meter Data(Day) Cleaned.csv")
    Linear_Regression(r"C:\Users\cruskowski\Desktop\Local Repository\Potable Water Meter Forecast\Data\Installed Meter Data(Day) Cleaned.csv")
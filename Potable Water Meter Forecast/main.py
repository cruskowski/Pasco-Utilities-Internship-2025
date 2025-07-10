from Analysis.Visualization import visualize_installed_by_month #package from analysis folder so we can use it
from Forecasting.LinearRRegression import Linear_Regression 

from Analysis.Basic import basic_analysis

if __name__ == "__main__":
    visualize_installed_by_month(r"C:\Users\cruskowski\Desktop\Local Repository\Potable Water Meter Forecast\Data\post_Installed Meter Data(Day) Cleaned.csv")
    Linear_Regression(r"C:\Users\cruskowski\Desktop\Local Repository\Potable Water Meter Forecast\Data\post_Installed Meter Data(Day) Cleaned.csv")
    basic_analysis(r"C:\Users\cruskowski\Desktop\Local Repository\Potable Water Meter Forecast\Data\post_Installed Meter Data(Day) Cleaned.csv")

    #visualize_installed_by_month(r"C:\Users\cruskowski\Desktop\Local Repository\Potable Water Meter Forecast\Data\post_Audit 2024 Raw Data Combined.csv")
    #Linear_Regression(r"C:\Users\cruskowski\Desktop\Local Repository\Potable Water Meter Forecast\Data\post_Audit 2024 Raw Data Combined.csv")
    #basic_analysis(r"C:\Users\cruskowski\Desktop\Local Repository\Potable Water Meter Forecast\Data\post_Audit 2024 Raw Data Combined.csv")
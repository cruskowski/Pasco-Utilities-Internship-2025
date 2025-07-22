from Analysis.Visualization import visualize_installed_by_month #package from analysis folder so we can use it
from Forecasting.LinearRRegression import Linear_Regression 

from Analysis.Basic import numberofuniqueaccounts

from Analysis.Basic import total_billedwater

if __name__ == "__main__":
    #visualize_installed_by_month(r"C:\Users\cruskowski\Desktop\Local Repository\Potable Water Meter Forecast\Data\post_Installed Meter Data(Day) Cleaned.csv")
    total_billedwater(r"C:\Users\cruskowski\Desktop\GitHub Local Repository\Pasco-Utilities-Internship-2025\Data Analysis\Potable Water Meter Analysis\Data\SECOND_Audit_2024_Single_Family_Only.csv")

    numberofuniqueaccounts(r"C:\Users\cruskowski\Desktop\GitHub Local Repository\Pasco-Utilities-Internship-2025\Data Analysis\Potable Water Meter Analysis\Data\SECOND_Audit_2024_Single_Family_Only.csv")

    #Linear_Regression(r"C:\Users\cruskowski\Desktop\Local Repository\Potable Water Meter Forecast\Data\post_Installed Meter Data(Day) Cleaned.csv")
    #basic_analysis(r"C:\Users\cruskowski\Desktop\Local Repository\Potable Water Meter Forecast\Data\post_Installed Meter Data(Day) Cleaned.csv")

    #visualize_installed_by_month(r"C:\Users\cruskowski\Desktop\Local Repository\Potable Water Meter Forecast\Data\post_Audit 2024 Raw Data Combined.csv")
    #Linear_Regression(r"C:\Users\cruskowski\Desktop\Local Repository\Potable Water Meter Forecast\Data\post_Audit 2024 Raw Data Combined.csv")
    #basic_analysis(r"C:\Users\cruskowski\Desktop\Local Repository\Potable Water Meter Forecast\Data\post_Audit 2024 Raw Data Combined.csv")
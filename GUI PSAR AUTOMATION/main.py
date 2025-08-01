from tools.xlsxConv import convert_xlsx_to_csv
from tools.combineCSV import combine_large_csvs_robust
from tools.meterConsumptionByRevClass import analyze_meter_consumption_by_revenue_class    
from tools.calculations import PSAR_Data
from tools.cleaningRemoving import cleaningRemovingFUNC
from tools.bulkMeterConsumption import bulkMeterConsumptionFUNC



if __name__ == "__main__":
    #xlsx_file = r'C:\Users\cruskowski\Desktop\PSAR AUTOMATION\Data_Pre\Audit 2023 Raw Data 2024.02.28.xlsx'
    #csv_file = r'C:\Users\cruskowski\Desktop\PSAR AUTOMATION\Data_Pre\CSV Raw.csv'
    #convert_xlsx_to_csv(xlsx_file, csv_file)

    file1_path = r'C:\Users\cruskowski\Desktop\PSAR AUTOMATION\Data_Pre\1 Audit 2023 Raw Data .csv'
    file2_path = r'C:\Users\cruskowski\Desktop\PSAR AUTOMATION\Data_Pre\2 Audit 2023 Raw Data .csv'
    file3_path = r'C:\Users\cruskowski\Desktop\GUI PSAR AUTOMATION\Data_Pre\3 Bulk Audit 2023 Raw Data.csv'
    output_path = r'C:\Users\cruskowski\Desktop\GUI PSAR AUTOMATION\Data_Post\3 Bulk Audit 2023 Raw Data.csv'

    #combine_large_csvs_robust(file1_path, file2_path, output_path)

    cleaningRemovingFUNC(output_path, file3_path)

    analyze_meter_consumption_by_revenue_class(output_path)

    bulktotal = bulkMeterConsumptionFUNC(file3_path)

    PSAR_Data(bulktotal)

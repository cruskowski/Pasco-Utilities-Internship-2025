import pandas as pd

#df = pd.read_csv('Installed Meter Data (Day).csv') # saves and reads csv file into a data frame(pandas primary data stucutre for handling tabular data)

df = pd.read_csv(r'C:\Users\cruskowski\Desktop\Local Repository\Potable Water Meter Forecast\Data\Installed Meter Data (Day).csv')

df_cleaned = df.dropna()    #dropna() removes all rows with any null values, df_cleaned = new data file with null values removed
df_cleaned.to_csv(r'C:\Users\cruskowski\Desktop\Local Repository\Potable Water Meter Forecast\Data\Installed Meter Data(Day) Cleaned.csv', index=False)
#df_cleaned.to_csv('Installed Meter Data(Day) Cleaned.csv', index=False) # saves dataframe to to new csv file, index=False ensures that the dataframes index is not written as a seperate column in the ouput file

print("First 5 rows of cleaned data:")    
print(df_cleaned.head())
print("/nLast 5 rows of cleaned data:")
print(df_cleaned.tail())
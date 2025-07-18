import pandas as pd

df = pd.read_csv(r'C:\Users\cruskowski\Desktop\GitHub Local Repository\Pasco-Utilities-Internship-2025\CIS_HALL_Data&Stats\Data\CIS_Hall_Data_sewer.csv')

def basicStats(df):

    title = df.columns[62]
    print("Stats for " + title)
    print("Number of Accounts: " + str(float(len(df))))
    total_Sum_High_Read = df['HIGH_READ_LIMIT'].sum()
    print("Total Sum of High Read Limit: " + str(float(total_Sum_High_Read)))
    total__Sum_Low_Read = df['LOW_READ_LIMIT'].sum()
    print("Total Sum of Low Read Limit: " + str(float(total__Sum_Low_Read)))
    Average_Low_Read = df['LOW_READ_LIMIT'].mean()
    print("Average Low Read Limit: " + str(float(Average_Low_Read)))
    Average_High_Read = df['HIGH_READ_LIMIT'].mean()
    print("Average High Read Limit: " + str(float(Average_High_Read)))

    # Define account_summary by grouping and aggregating
    account_summary = df.groupby(['ACCOUNT_ID', 'ACCOUNT_FULL_NAME'], as_index=False).agg(
        SUM_HIGH_READ_LIMIT=pd.NamedAgg(column='HIGH_READ_LIMIT', aggfunc='sum')
    )

    print(f"\nTOP 10 ACCOUNTS BY HIGH READ LIMIT:")
    top_10_high = account_summary.nlargest(10, 'SUM_HIGH_READ_LIMIT')
    print(f"{'ACCOUNT_ID':<12} {'ACCOUNT_NAME':<35} {'SUM_HIGH_LIMIT':<15}")
    print("-" * 70)
    for _, row in top_10_high.iterrows():
        account_name = str(row['ACCOUNT_FULL_NAME'])[:30] + "..." if len(str(row['ACCOUNT_FULL_NAME'])) > 30 else str(row['ACCOUNT_FULL_NAME'])
        print(f"{row['ACCOUNT_ID']:<12} {account_name:<35} {row['SUM_HIGH_READ_LIMIT']:<15}")

if __name__ == "__main__":
    basicStats(df)

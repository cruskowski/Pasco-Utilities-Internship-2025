import pandas as pd

# Global variables to store consumption totals by revenue class description
SINGLE_FAMILY = 0
MULTI_FAMILY = 0
RETAIL = 0
OTHER = 0
IRRIGATION = 0
HYDRANT_METERS = 0
SERVICE = 0
SINGLE_FAM_MOBILE_IN_PARK = 0
OFFICE = 0
MEDICAL = 0
R_V_PARKS = 0
EDUCATION = 0
RECREATION = 0
HOSPITAL = 0
SINGLE_FAMILY_MOBILE = 0
FULL_SERV_RESTAURANT = 0
NURSING_HOME = 0
WHOLESALE = 0
SINGLE_SERVE_RESTAURANT = 0
CHURCH_VETERINARIAN = 0
COVER_CARD = 0
LAUNDROMAT = 0
CLINICS = 0
EFFLUENT = 0
DAYCARE = 0
FOOD_HANDLER = 0
DO_NOT_COUNT = 0
BULK = 0

def analyze_meter_consumption_by_revenue_class(csv_file):
    """
    Calculate total billed meter consumption by revenue class description
    and store in global variables
    """
    global SINGLE_FAMILY, MULTI_FAMILY, RETAIL, OTHER, IRRIGATION, HYDRANT_METERS, SERVICE
    global SINGLE_FAM_MOBILE_IN_PARK, OFFICE, MEDICAL, R_V_PARKS, EDUCATION, RECREATION
    global HOSPITAL, SINGLE_FAMILY_MOBILE, FULL_SERV_RESTAURANT, NURSING_HOME, WHOLESALE
    global SINGLE_SERVE_RESTAURANT, CHURCH_VETERINARIAN, COVER_CARD, LAUNDROMAT, CLINICS
    global EFFLUENT, DAYCARE, FOOD_HANDLER, DO_NOT_COUNT, BULK
    global NULL

    try:
        # Read the CSV file with low_memory=False to handle mixed types
        df = pd.read_csv(csv_file, low_memory=False)
        
        # Convert BILLED METER CONSUMPTION to numeric, handling any non-numeric values
        df['BILLED METER CONSUMPTION'] = pd.to_numeric(df['BILLED METER CONSUMPTION'], errors='coerce')
        
        # Group by REVENUE CLASS DESCRIPTION and sum BILLED METER CONSUMPTION
        consumption_by_class = df.groupby('REVENUE CLASS DESCRIPTION')['BILLED METER CONSUMPTION'].sum().sort_values(ascending=False)
        
        # Reset all global variables
        SINGLE_FAMILY = 0
        MULTI_FAMILY = 0
        RETAIL = 0
        OTHER = 0
        IRRIGATION = 0
        HYDRANT_METERS = 0
        SERVICE = 0
        SINGLE_FAM_MOBILE_IN_PARK = 0
        OFFICE = 0
        MEDICAL = 0
        R_V_PARKS = 0
        EDUCATION = 0
        RECREATION = 0
        HOSPITAL = 0
        SINGLE_FAMILY_MOBILE = 0
        FULL_SERV_RESTAURANT = 0
        NURSING_HOME = 0
        WHOLESALE = 0
        SINGLE_SERVE_RESTAURANT = 0
        CHURCH_VETERINARIAN = 0
        COVER_CARD = 0
        LAUNDROMAT = 0
        CLINICS = 0
        EFFLUENT = 0
        DAYCARE = 0
        FOOD_HANDLER = 0
        DO_NOT_COUNT = 0
        BULK = 0
        NULL = 0  
        
        # Assign consumption values to global variables based on exact matches
        for revenue_class, consumption in consumption_by_class.items():
            if revenue_class == 'SINGLE FAMILY':
                SINGLE_FAMILY = consumption
            elif revenue_class == 'MULTI FAMILY':
                MULTI_FAMILY = consumption
            elif revenue_class == 'RETAIL':
                RETAIL = consumption
            elif revenue_class == 'OTHER':
                OTHER = consumption
            elif revenue_class == 'IRRIGATION':
                IRRIGATION = consumption
            elif revenue_class == 'HYDRANT METERS':
                HYDRANT_METERS = consumption
            elif revenue_class == 'SERVICE':
                SERVICE = consumption
            elif revenue_class == 'SINGLE FAM MOBILE IN PARK':
                SINGLE_FAM_MOBILE_IN_PARK = consumption
            elif revenue_class == 'OFFICE':
                OFFICE = consumption
            elif revenue_class == 'MEDICAL':
                MEDICAL = consumption
            elif revenue_class == 'R V PARKS':
                R_V_PARKS = consumption
            elif revenue_class == 'EDUCATION':
                EDUCATION = consumption
            elif revenue_class == 'RECREATION':
                RECREATION = consumption
            elif revenue_class == 'HOSPITAL':
                HOSPITAL = consumption
            elif revenue_class == 'SINGLE FAMILY MOBILE':
                SINGLE_FAMILY_MOBILE = consumption
            elif revenue_class == 'FULL SERV RESTAURANT':
                FULL_SERV_RESTAURANT = consumption
            elif revenue_class == 'NURSING HOME':
                NURSING_HOME = consumption
            elif revenue_class == 'WHOLESALE':
                WHOLESALE = consumption
            elif revenue_class == 'SINGLE SERVE RESTAURANT':
                SINGLE_SERVE_RESTAURANT = consumption
            elif revenue_class == 'CHURCH/VETERINARIAN':
                CHURCH_VETERINARIAN = consumption
            elif revenue_class == 'COVER CARD':
                COVER_CARD = consumption
            elif revenue_class == 'LAUNDROMAT':
                LAUNDROMAT = consumption
            elif revenue_class == 'CLINICS':
                CLINICS = consumption
            elif revenue_class == 'EFFLUENT':
                EFFLUENT = consumption
            elif revenue_class == 'Daycare':
                DAYCARE = consumption
            elif revenue_class == 'Food Handler':
                FOOD_HANDLER = consumption
            elif revenue_class == 'DO NOT COUNT':
                DO_NOT_COUNT = consumption
            elif revenue_class == 'BULK':
                BULK = consumption
            elif revenue_class == 'NULL':
                NULL = consumption

        # Display results
        print("Revenue Class Description | Total Consumption")
        print("-" * 50)
        
        total_consumption = 0
        for revenue_class, consumption in consumption_by_class.items():
            print(f"{revenue_class:<30} | {consumption:>15,}")
            total_consumption += consumption
        
        print("-" * 50)
        print(f"{'TOTAL':<30} | {total_consumption:>15,}")
        
    except FileNotFoundError:
        print(f"Error: File {csv_file} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Default file path for testing
    csv_file = r'C:\Users\cruskowski\Desktop\PSAR AUTOMATION\Data_Pre\CSV Combined.csv'
    analyze_meter_consumption_by_revenue_class(csv_file)
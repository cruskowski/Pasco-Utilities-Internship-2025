from . import meterConsumptionByRevClass

def PSAR_Data(bulktotal):
    """
    Perform PSAR data calculations using the global variables from meterConsumptionByRevClass
    """
    #print("Running PSAR Data calculations...")
    bulktotal = bulktotal
    SINGLE_FAMILY = meterConsumptionByRevClass.SINGLE_FAMILY
    MULTI_FAMILY = meterConsumptionByRevClass.MULTI_FAMILY
    SINGLE_FAMILY_MOBILE = meterConsumptionByRevClass.SINGLE_FAMILY_MOBILE
    SINGLE_FAM_MOBILE_IN_PARK = meterConsumptionByRevClass.SINGLE_FAM_MOBILE_IN_PARK
    R_V_PARKS = meterConsumptionByRevClass.R_V_PARKS
    RETAIL = meterConsumptionByRevClass.RETAIL
    OFFICE = meterConsumptionByRevClass.OFFICE
    MEDICAL = meterConsumptionByRevClass.MEDICAL
    EDUCATION = meterConsumptionByRevClass.EDUCATION
    HOSPITAL = meterConsumptionByRevClass.HOSPITAL
    FULL_SERV_RESTAURANT = meterConsumptionByRevClass.FULL_SERV_RESTAURANT
    NURSING_HOME = meterConsumptionByRevClass.NURSING_HOME
    SINGLE_SERVE_RESTAURANT = meterConsumptionByRevClass.SINGLE_SERVE_RESTAURANT
    CHURCH_VETERINARIAN = meterConsumptionByRevClass.CHURCH_VETERINARIAN
    LAUNDROMAT = meterConsumptionByRevClass.LAUNDROMAT
    CLINICS = meterConsumptionByRevClass.CLINICS
    DAYCARE = meterConsumptionByRevClass.DAYCARE
    FOOD_HANDLER = meterConsumptionByRevClass.FOOD_HANDLER
    BULK = meterConsumptionByRevClass.BULK
    IRRIGATION = meterConsumptionByRevClass.IRRIGATION
    HYDRANT_METERS = meterConsumptionByRevClass.HYDRANT_METERS
    SERVICE = meterConsumptionByRevClass.SERVICE
    OTHER = meterConsumptionByRevClass.OTHER
    EFFLUENT = meterConsumptionByRevClass.EFFLUENT
    WHOLESALE = meterConsumptionByRevClass.WHOLESALE
    COVER_CARD = meterConsumptionByRevClass.COVER_CARD
    RECREATION = meterConsumptionByRevClass.RECREATION
    NULL = meterConsumptionByRevClass.NULL
    
    # Calculate PSAR categories
    print("=== PSAR DATA CALCULATIONS ===\n")
    
    # Single Family Dwelling Units
    single_family_units = SINGLE_FAMILY + SINGLE_FAMILY_MOBILE + NULL + COVER_CARD
    print(f"Single Family Dwelling Units: {((single_family_units)*1000)/365:,.0f}")

    # Multiple Family Dwelling Units
    multiple_family_units = MULTI_FAMILY
    print(f"Multiple Family Dwelling Units: {((multiple_family_units)*1000)/365:,.0f}")

    # Mobile Home Dwelling Units
    mobile_home_units = SINGLE_FAM_MOBILE_IN_PARK
    print(f"Mobile Home Dwelling Units: {((mobile_home_units)*1000)/365:,.0f}")

    # Residential Irrigation Accounts
    residential_irrigation = 0
    print(f"Residential Irrigation Accounts: {((residential_irrigation)*1000)/365:,.0f}")

    # Subtotal of Residential Service
    subtotal_residential = single_family_units + multiple_family_units + mobile_home_units + residential_irrigation
    print(f"Subtotal of Residential Service: {((subtotal_residential)*1000)/365:,.0f}")

    # Industrial/Commercial Uses
    industrial_commercial = (RETAIL + OFFICE + MEDICAL + HOSPITAL + FULL_SERV_RESTAURANT + NURSING_HOME + SINGLE_SERVE_RESTAURANT + CHURCH_VETERINARIAN + LAUNDROMAT + CLINICS + DAYCARE + FOOD_HANDLER + WHOLESALE + EDUCATION + HYDRANT_METERS + SERVICE + OTHER)
    print(f"Industrial/Commercial Uses: {((((industrial_commercial)*1000)-(bulktotal))/365):,.0f}")

    # Agricultural Uses
    agricultural = 0  # Assuming BULK represents agricultural uses
    print(f"Agricultural Uses: {((agricultural)*1000)/365:,.0f}")

    # Recreational/Aesthetic Uses
    recreational_aesthetic = IRRIGATION + RECREATION + EFFLUENT + R_V_PARKS
    print(f"Recreational/Aesthetic Uses: {((recreational_aesthetic)*1000)/365:,.0f}")

    # Golf Course Irrigation (if any - might need to be identified separately)
    golf_course = 0  # This might need to be separated from other categories
    print(f"Golf Course Irrigation: {((golf_course)*1000)/365:,.0f}")

    # Fire and Other Accounted Uses
    fire_other = 0
    print(f"Fire and Other Accounted Uses: {((fire_other)*1000)/365:,.0f}")

    total_consumption = (subtotal_residential + industrial_commercial + agricultural + 
                        recreational_aesthetic + golf_course + fire_other)
    print(f"\nSUBTOTAL: {((total_consumption)*1000)/365:,.0f}")

    return {
        'single_family_units': single_family_units,
        'multiple_family_units': multiple_family_units,
        'mobile_home_units': mobile_home_units,
        'residential_irrigation': residential_irrigation,
        'subtotal_residential': subtotal_residential,
        'industrial_commercial': industrial_commercial,
        'agricultural': agricultural,
        'recreational_aesthetic': recreational_aesthetic,
        'golf_course': golf_course,
        'fire_other': fire_other,
        'total': total_consumption
    }


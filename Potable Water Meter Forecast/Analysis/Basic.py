import pandas as pd


def basic_analysis(csv_path):
    df = pd.read_csv(csv_path, parse_dates=['Date'])
    metersizedesc4_counts = df['MeterSizeDesc4'].value_counts()
    total_meters = len(df)

    # Create a variable for each meter size type
    for meter_size, count in metersizedesc4_counts.items():
        var_name = meter_size.replace(" ", "_").replace("/", "_").replace("\\", "_")
        globals()[var_name] = count
        print(f"{var_name} = {count}")

    # Multiplication based on meter size
    multipliers = {
        '_5_8___3_4': 215,
        '2': 1720,
        '1': 538,
        '1.5': 1072,
        '3': 3225,
        '6': 10750,
        '8': 17200,
        '4': 5375,
        '12': 1
    }

    results = {}
    for key, multiplier in multipliers.items():
        if key in globals():
            results[key] = globals()[key] * multiplier

    for k, v in results.items():
        print(f"{k} multiplied = {v}")

    total_product_sum = sum(results.values())
    print(f"Sum of all products: {total_product_sum}")

    # Sum by Meter Type (Water or Reuse)
    meter_type_products = {}
    for meter_type in df['Meter Type'].unique():
        subset = df[df['Meter Type'] == meter_type]
        subset_counts = subset['MeterSizeDesc4'].value_counts()
        subtotal = 0
        for meter_size, count in subset_counts.items():
            key = meter_size.replace(" ", "_").replace("/", "_").replace("\\", "_")
            if key in multipliers:
                subtotal += count * multipliers[key]
        meter_type_products[meter_type] = subtotal
        print(f"Sum of products for {meter_type}: {subtotal}")

    print(f"Total meters: {total_meters}")

#def basic_total(csv_path):
    



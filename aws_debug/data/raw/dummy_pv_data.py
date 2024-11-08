import pandas as pd
import numpy as np


def process_and_interpolate(csv_file, column_to_extract, output_file):
    # Step 1: Read the CSV and extract the required column
    df = pd.read_csv(csv_file, usecols=[column_to_extract])
    # Step 2: Apply a division of 1000 to all rows in the extracted column
    df[column_to_extract] = df[column_to_extract] / 1000
    # Step 3: Create a timestamp with hourly intervals (assuming it's sequential data)
    df['Timestamp'] = pd.date_range(
        start='2022-01-01 00:00', periods=len(df), freq='H')

    # Step 4: Set the Timestamp column as the index for interpolation
    df.set_index('Timestamp', inplace=True)

    # Step 5: Resample to a 30-minute frequency and interpolate
    df_30min = df.resample('30T').interpolate(method='linear')

    # Step 6: Add a timestamp label for each row
    df_30min.reset_index(inplace=True)

    # Save the result to CSV
    df_30min.to_csv(output_file, index=False)
    print(f"Interpolated data saved to {output_file}")


# Parameters
# Path to the input CSV file
csv_file = "Timeseries_51.823_0.103_SA3_2kWp_crystSi_14_39deg_-5deg_2012_2013.csv"
column_to_extract = "P"  # Column name to extract and process
output_file = "interpolated_pv_dummy_data.csv"  # Path to the output CSV file

# Run the function
process_and_interpolate(csv_file, column_to_extract, output_file)

import pandas as pd
import os


def filter_and_group_by_id(csv_file, id_column, columns_to_read, output_folder):
    # Step 1: Read specific columns from the CSV
    df = pd.read_csv(csv_file, usecols=columns_to_read)

    # Step 2: Group by the specified ID column
    grouped = df.groupby(id_column, group_keys=True)

    # Step 4: Save each group as a separate CSV
    for group_id, group_df in grouped:
        # Define the file name for each group
        output_file = os.path.join(
            output_folder, f"{id_column}_{group_id}.csv")
        group_df.to_csv(output_file, index=False)
        print(f"Saved group '{group_id}' to {output_file}")
    # Show the result to the user
    return grouped


# Parameters
# Path to your CSV file          # Keyword to filter rows by
csv_file = "londonData_reduced.csv"
id_column = "LCLid"                   # Column to group by
# List of columns to read (ID + relevant ones)              # Column to group by
columns_to_read = ["LCLid", "KWH/hh (per half hour)"]
output_folder = "data"

# Run the function
result_df = filter_and_group_by_id(
    csv_file, id_column, columns_to_read, output_folder)
print(result_df["MAC000002"])

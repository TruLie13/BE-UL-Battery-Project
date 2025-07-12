import pandas as pd
import os

print("--- Starting Data File Analysis ---")

# Define the directories to scan
data_dirs = [
    os.path.join('data', 'normal_voltage'),
    os.path.join('data', 'reduced_voltage'),
]

total_files_processed = 0
all_results = []

# Loop through each directory
for directory in data_dirs:
    if not os.path.isdir(directory):
        print(f"\nWARNING: Directory not found, skipping: {directory}")
        continue

    print(f"\n--- Scanning Directory: {directory} ---")

    # Loop through each file in the directory
    for filename in os.listdir(directory):
        if filename.endswith(('.xls', '.xlsx')):
            total_files_processed += 1
            file_path = os.path.join(directory, filename)

            try:
                # Load all sheets from the Excel file into a dictionary of DataFrames
                all_sheets = pd.read_excel(file_path, sheet_name=None)
                # Concatenate them all into a single DataFrame
                df = pd.concat(all_sheets.values(), ignore_index=True)

                # Get the total number of rows (data points)
                total_data_points = len(df)

                # Get the number of unique cycles from the 'Cycle_Index' column
                # This is more robust than just getting the max value
                total_cycles = df['Cycle_Index'].nunique()

                all_results.append({
                    "filename": filename,
                    "cycles": total_cycles,
                    "data_points": total_data_points
                })

            except Exception as e:
                print(f"ERROR processing {filename}: {e}")

# Print the results in a formatted table
if all_results:
    print("\n--- Analysis Results ---")
    # Find the longest filename for alignment
    max_len = max(len(res['filename']) for res in all_results) + 2

    # Print header
    print(f"{'Filename'.ljust(max_len)}{'Total Cycles'.ljust(15)}{'Total Data Points'}")
    print(f"{'-' * (max_len - 1)} {'-' * 14} {'-' * 17}")

    for res in sorted(all_results, key=lambda x: x['filename']):
        print(
            f"{res['filename'].ljust(max_len)}{str(res['cycles']).ljust(15)}{res['data_points']}")

    # --- This is the new section to calculate and print totals ---
    grand_total_cycles = sum(res['cycles'] for res in all_results)
    grand_total_data_points = sum(res['data_points'] for res in all_results)

    print(f"{'-' * (max_len - 1)} {'-' * 14} {'-' * 17}")
    print(f"{'GRAND TOTAL'.ljust(max_len)}{str(grand_total_cycles).ljust(15)}{grand_total_data_points}")
    # --- End of new section ---

print("\n---------------------------------")
print(f"Total files processed: {total_files_processed}")
print("--- Script Finished ---")

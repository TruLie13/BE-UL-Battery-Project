# test_load.py
import pandas as pd
import os

print("Script started...")

# Define the path to the file
file_path = os.path.join('data', 'normal_voltage',
                         'Ba01_N20_OV1_300, 20% CF, 300 Cycles.xls')

print(f"Attempting to load file: {file_path}")

# Read the data from the Excel file
try:
    df = pd.read_excel(file_path)
    print("File loaded successfully!")

    print("\n--- First 5 Rows ---")
    print(df.head())

    print("\n--- Column Names ---")
    print(df.columns)

except FileNotFoundError:
    print(f"ERROR: File not found at path: {file_path}")
    print(f"Current working directory is: {os.getcwd()}")
except Exception as e:
    print(f"An error occurred: {e}")

print("\nScript finished.")

import os
import re
import pandas as pd
from django.core.management.base import BaseCommand
from core.models import Battery, CycleData


class Command(BaseCommand):
    help = 'Loads data from Excel files into the database'

    def handle(self, *args, **kwargs):
        # Path to the directory containing the data files
        data_dir = os.path.join('data', 'normal_voltage')

        self.stdout.write(f"Looking for files in {data_dir}...")

        # Loop through all files in the directory
        for filename in os.listdir(data_dir):
            if not filename.endswith('.xls'):
                continue  # Skip files that are not Excel files

            self.stdout.write(f"Processing file: {filename}...")

            # Extract the battery number from the filename
            battery_num = None
            match = re.search(r'Ba(\d+)_', filename)
            if match:
                battery_num = int(match.group(1))

            # --- 1. Get or Create the Battery record ---
            # Thisprevents duplicate batteries if the script gets ran again
            battery, created = Battery.objects.get_or_create(
                file_name=filename,
                defaults={'battery_number': battery_num}
            )

            if not created and battery.battery_number != battery_num:
                battery.battery_number = battery_num
                battery.save()

            if created:
                self.stdout.write(self.style.SUCCESS(
                    f"  Created new battery: {filename}"))
            else:
                self.stdout.write(f"  Found existing battery: {filename}")

            # --- 2. Read the Excel file with Pandas ---
            file_path = os.path.join(data_dir, filename)
            df = pd.read_excel(file_path)

            # --- 3. Clean and Prepare the Data ---
            # Your temperature column is 'Temperature (C)_1'. Let's rename it for easier use.
            df.rename(
                columns={'Temperature (C)_1': 'temperature_c'}, inplace=True)

            # Ensure Cycle_Index is treated as a number
            df['Cycle_Index'] = pd.to_numeric(
                df['Cycle_Index'], errors='coerce')
            df.dropna(subset=['Cycle_Index'], inplace=True)
            df['Cycle_Index'] = df['Cycle_Index'].astype(int)

            # --- 4. Group by Cycle and Aggregate Data ---
            # For each cycle, we want the max discharge capacity and the avg/max temperature
            cycle_summary = df.groupby('Cycle_Index').agg(
                discharge_capacity=('Discharge_Capacity(Ah)', 'max'),
                charge_capacity=('Charge_Capacity(Ah)', 'max'),
                avg_temp=('temperature_c', 'mean'),
                max_temp=('temperature_c', 'max'),
                min_temp=('temperature_c', 'min')
            ).reset_index()

            # --- 5. Load the Summarized Data into the Database ---
            self.stdout.write(
                f"  Loading {len(cycle_summary)} cycles into database...")
            for index, row in cycle_summary.iterrows():
                CycleData.objects.update_or_create(
                    battery=battery,
                    cycle_number=row['Cycle_Index'],
                    defaults={
                        'discharge_capacity': row['discharge_capacity'],
                        'charge_capacity': row['charge_capacity'],
                        'avg_temp': row['avg_temp'],
                        'max_temp': row['max_temp'],
                        'min_temp': row['min_temp'],
                    }
                )

            self.stdout.write(self.style.SUCCESS(
                f"  Successfully processed {filename}"))

        self.stdout.write(self.style.SUCCESS("\nData loading complete!"))

import os
import re
import pandas as pd
from django.core.management.base import BaseCommand
from core.models import Battery, CycleData


class Command(BaseCommand):
    """
    This command loads battery cycle data from Excel files located in specified
    subdirectories of the 'data' folder. It populates the Battery and
    CycleData models in the database.
    """
    help = 'Loads data from Excel files into the database'

    def handle(self, *args, **kwargs):
        # 1. Define the data directories and their corresponding types
        voltage_dirs = {
            'normal': os.path.join('data', 'normal_voltage'),
            'reduced': os.path.join('data', 'reduced_voltage'),
        }

        # 2. Loop through each directory
        for v_type, data_dir in voltage_dirs.items():
            if not os.path.isdir(data_dir):
                self.stdout.write(self.style.WARNING(
                    f"Directory not found, skipping: {data_dir}"))
                continue

            self.stdout.write(f"--- Processing directory: {data_dir} ---")

            for filename in os.listdir(data_dir):
                if not filename.endswith(('.xls', '.xlsx')):
                    continue

                self.stdout.write(f"Processing file: {filename}...")

                # 3. Extract the battery number from the filename
                battery_num = None
                # This regex looks for 'Ba' followed by one or more digits
                match = re.search(r'B[ab](\d+)_', filename)
                if match:
                    battery_num = int(match.group(1))

                # 4. Get or Update the Battery record in the database
                try:
                    battery = Battery.objects.get(file_name=filename)
                    # If found, ensure its details are up-to-date
                    battery.battery_number = battery_num
                    battery.voltage_type = v_type
                    battery.save()
                    created = False
                except Battery.DoesNotExist:
                    # If not found, create a new record
                    battery = Battery.objects.create(
                        file_name=filename,
                        battery_number=battery_num,
                        voltage_type=v_type
                    )
                    created = True

                if created:
                    self.stdout.write(self.style.SUCCESS(
                        f"  Created new battery: {filename}"))
                else:
                    self.stdout.write(
                        f"  Found and updated existing battery: {filename}")

                # 5. Read and process the cycle data from the Excel file
                file_path = os.path.join(data_dir, filename)
                df = pd.read_excel(file_path)

                # Clean column names for consistency
                df.rename(
                    columns={'Temperature (C)_1': 'temperature_c'}, inplace=True)

                # Ensure Cycle_Index is a clean integer
                df['Cycle_Index'] = pd.to_numeric(
                    df['Cycle_Index'], errors='coerce')
                df.dropna(subset=['Cycle_Index'], inplace=True)
                df['Cycle_Index'] = df['Cycle_Index'].astype(int)

                # 6. Aggregate the data by cycle
                cycle_summary = df.groupby('Cycle_Index').agg(
                    discharge_capacity=('Discharge_Capacity(Ah)', 'max'),
                    charge_capacity=('Charge_Capacity(Ah)', 'max'),
                    avg_temp=('temperature_c', 'mean'),
                    max_temp=('temperature_c', 'max'),
                    min_temp=('temperature_c', 'min')
                ).reset_index()

                # 7. Load the summarized cycle data into the database
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
                    f"  Successfully processed {filename}\n"))

        self.stdout.write(self.style.SUCCESS("--- Data loading complete! ---"))

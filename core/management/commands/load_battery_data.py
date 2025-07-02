import os
import re
import pandas as pd
from django.core.management.base import BaseCommand
from django.db.models import Avg
from core.models import Battery, CycleData


class Command(BaseCommand):
    """
    This command loads battery cycle data from Excel files and then calculates
    and saves summary performance statistics for each battery.
    """
    help = 'Loads and processes all battery data from Excel files.'

    def handle(self, *args, **kwargs):
        # --- PHASE 1: LOAD RAW CYCLE DATA ---
        self.stdout.write(self.style.SUCCESS(
            "--- Phase 1: Ingesting Cycle Data from Excel Files ---"))

        voltage_dirs = {
            'normal': os.path.join('data', 'normal_voltage'),
            'reduced': os.path.join('data', 'reduced_voltage'),
        }

        for v_type, data_dir in voltage_dirs.items():
            if not os.path.isdir(data_dir):
                self.stdout.write(self.style.WARNING(
                    f"Directory not found, skipping: {data_dir}"))
                continue

            self.stdout.write(f"Processing directory: {data_dir}")

            for filename in os.listdir(data_dir):
                if not filename.endswith(('.xls', '.xlsx')):
                    continue

                parts = filename.split('_')
                c_rate_val = parts[1] if len(parts) > 1 else None
                stress_test_val = parts[2] if len(parts) > 2 else None
                match = re.search(r'B[ab](\d+)_', filename)
                battery_num = int(match.group(1)) if match else None

                battery, created = Battery.objects.update_or_create(
                    file_name=filename,
                    defaults={
                        'battery_number': battery_num,
                        'voltage_type': v_type,
                        'c_rate': c_rate_val,
                        'stress_test': stress_test_val
                    }
                )

                all_sheets = pd.read_excel(os.path.join(
                    data_dir, filename), sheet_name=None)
                df = pd.concat(all_sheets.values(), ignore_index=True)

                df.rename(
                    columns={'Temperature (C)_1': 'temperature_c'}, inplace=True)
                df['Cycle_Index'] = pd.to_numeric(
                    df['Cycle_Index'], errors='coerce')
                df.dropna(subset=['Cycle_Index'], inplace=True)
                df['Cycle_Index'] = df['Cycle_Index'].astype(int)

                cycle_summary = df.groupby('Cycle_Index').agg(
                    discharge_capacity=('Discharge_Capacity(Ah)', 'max'),
                    charge_capacity=('Charge_Capacity(Ah)', 'max'),
                    avg_current=('Current(A)', 'mean'),
                    avg_voltage=('Voltage(V)', 'mean'),
                    avg_temp=('temperature_c', 'mean'),
                    max_temp=('temperature_c', 'max'),
                    min_temp=('temperature_c', 'min')
                ).reset_index()

                battery.cycle_count = len(cycle_summary)
                battery.save(update_fields=['cycle_count'])

                for index, row in cycle_summary.iterrows():
                    CycleData.objects.update_or_create(
                        battery=battery,
                        cycle_number=row['Cycle_Index'],
                        defaults={
                            'discharge_capacity': row['discharge_capacity'],
                            'charge_capacity': row['charge_capacity'],
                            'avg_current': row['avg_current'],
                            'avg_voltage': row['avg_voltage'],
                            'avg_temp': row['avg_temp'],
                            'max_temp': row['max_temp'],
                            'min_temp': row['min_temp'],
                        }
                    )

        # --- PHASE 2: CALCULATE AND SAVE SUMMARY STATISTICS ---
        self.stdout.write(self.style.SUCCESS(
            "\n--- Phase 2: Calculating and Saving Summary Statistics ---"))

        batteries = Battery.objects.all()
        summary_data = []

        for battery in batteries:
            cycles = battery.cycles.filter(discharge_capacity__gt=0)
            if not cycles.exists():
                continue

            first_cycle = cycles.earliest('cycle_number')
            last_cycle = cycles.latest('cycle_number')
            soh = round((last_cycle.discharge_capacity / first_cycle.discharge_capacity)
                        * 100, 2) if first_cycle.discharge_capacity > 0 else 0

            aggregates = battery.cycles.all().aggregate(avg_temp=Avg(
                'avg_temp'), avg_discharge=Avg('discharge_capacity'))

            summary_data.append({
                'id': battery.id,
                'cycle_count': battery.cycle_count or 0,
                'state_of_health': soh,
                'overall_avg_temp': aggregates.get('avg_temp') or 0,
                'overall_avg_discharge': aggregates.get('avg_discharge') or 0,
            })

        if not summary_data:
            self.stdout.write(self.style.WARNING(
                "No summary data to process for ranking."))
            return

        df = pd.DataFrame(summary_data).set_index('id')

        soh_range = df['state_of_health'].max() - df['state_of_health'].min()
        cycles_range = df['cycle_count'].max() - df['cycle_count'].min()

        df['norm_soh'] = (df['state_of_health'] - df['state_of_health'].min()
                          ) / soh_range if soh_range > 0 else 0.5
        df['norm_cycles'] = (df['cycle_count'] - df['cycle_count'].min()
                             ) / cycles_range if cycles_range > 0 else 0.5

        df['durability_score'] = (
            df['norm_cycles'] * 0.7 + df['norm_soh'] * 0.3).round(4)
        df['resilience_score'] = (
            df['norm_cycles'] * 0.3 + df['norm_soh'] * 0.7).round(4)
        df['balanced_score'] = (
            df['norm_cycles'] * 0.5 + df['norm_soh'] * 0.5).round(4)

        for battery_id, row in df.iterrows():
            Battery.objects.filter(pk=battery_id).update(
                state_of_health=row['state_of_health'],
                overall_avg_temp=round(row['overall_avg_temp'], 2),
                overall_avg_discharge=round(row['overall_avg_discharge'], 2),
                durability_score=row['durability_score'],
                resilience_score=row['resilience_score'],
                balanced_score=row['balanced_score']
            )

        self.stdout.write(self.style.SUCCESS(
            "--- All calculations complete and saved! ---"))

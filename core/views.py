from rest_framework import generics
from rest_framework.response import Response
from .models import Battery
from .serializers import BatterySerializer, BatterySummarySerializer
import pandas as pd


class BatteryList(generics.ListAPIView):
    serializer_class = BatterySerializer

    def get_queryset(self):
        voltage_type = self.kwargs['voltage_type']
        return Battery.objects.filter(voltage_type=voltage_type)


class BatteryDetail(generics.RetrieveAPIView):
    queryset = Battery.objects.all()
    serializer_class = BatterySerializer

    def get_object(self):
        queryset = self.get_queryset()
        obj = generics.get_object_or_404(
            queryset,
            voltage_type=self.kwargs['voltage_type'],
            battery_number=self.kwargs['battery_number']
        )
        return obj


class BatterySummaryView(generics.ListAPIView):
    queryset = Battery.objects.order_by('voltage_type', 'battery_number')
    serializer_class = BatterySummarySerializer
    ordering = ['voltage_type', 'battery_number']

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer_instance = self.get_serializer()

        # 1. Manually build a list of dictionaries with the initial data
        initial_data = []
        for battery in queryset:
            all_cycles = battery.cycles.all()
            avg_temp = None
            avg_discharge = None
            if all_cycles.exists():
                from django.db.models import Avg
                aggregates = all_cycles.aggregate(
                    avg_temp=Avg('avg_temp'),
                    avg_discharge=Avg('discharge_capacity')
                )
                avg_temp = aggregates.get('avg_temp')
                avg_discharge = aggregates.get('avg_discharge')

            soh = serializer_instance.get_state_of_health(battery)
            initial_data.append({
                'id': battery.id,
                'file_name': battery.file_name,
                'battery_number': battery.battery_number,
                'voltage_type': battery.voltage_type,
                'cycle_count': battery.cycle_count,
                'state_of_health': soh if soh is not None else 0,
                'overall_avg_temp': round(avg_temp, 2) if avg_temp is not None else None,
                'overall_avg_discharge': round(avg_discharge, 2) if avg_discharge is not None else None,
            })

        if not initial_data:
            return Response([])

        # 2. Use pandas to calculate the rankings
        df = pd.DataFrame(initial_data)

        # Normalization (with protection against division by zero)
        soh_range = df['state_of_health'].max() - df['state_of_health'].min()
        cycles_range = df['cycle_count'].max() - df['cycle_count'].min()

        df['norm_soh'] = (df['state_of_health'] - df['state_of_health'].min()
                          ) / soh_range if soh_range > 0 else 0.5
        df['norm_cycles'] = (df['cycle_count'] - df['cycle_count'].min()
                             ) / cycles_range if cycles_range > 0 else 0.5

        # 3. Calculate the different weighted scores (.7 and .3 are arbitrary, may update)
        df['durability_score'] = df['norm_cycles'] * 0.7 + df['norm_soh'] * 0.3
        df['resilience_score'] = df['norm_cycles'] * 0.3 + df['norm_soh'] * 0.7
        df['balanced_score'] = df['norm_cycles'] * 0.5 + df['norm_soh'] * 0.5

        # 4. Round columns
        df = df.round({
            'state_of_health': 2,
            'overall_avg_temp': 2,
            'overall_avg_discharge': 2,
            'durability_score': 4,
            'resilience_score': 4,
            'balanced_score': 4
        })

        # Clean up by dropping the temporary normalization columns
        df = df.drop(columns=['norm_soh', 'norm_cycles'])

        # Fill any potential NaN values with 0
        final_data = df.fillna(0).to_dict('records')

        return Response(final_data)

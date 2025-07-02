from rest_framework import serializers
from .models import Battery, CycleData


class CycleDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CycleData
        fields = ['cycle_number', 'discharge_capacity', 'charge_capacity', 'avg_current',
                  'avg_voltage', 'avg_temp', 'max_temp', 'min_temp']


class BatterySerializer(serializers.ModelSerializer):
    cycles = CycleDataSerializer(many=True, read_only=True)

    class Meta:
        model = Battery
        fields = ['id', 'file_name', 'cycle_count', 'cycles']


class BatterySummarySerializer(serializers.ModelSerializer):
    state_of_health = serializers.SerializerMethodField()
    durability_score = serializers.FloatField()
    resilience_score = serializers.FloatField()
    balanced_score = serializers.FloatField()
    overall_avg_temp = serializers.FloatField()
    overall_avg_discharge = serializers.FloatField()

    class Meta:
        model = Battery
        fields = [
            'id',
            'file_name',
            'battery_number',
            'voltage_type',
            'c_rate',
            'stress_test',
            'cycle_count',
            'state_of_health',
            'durability_score',
            'resilience_score',
            'balanced_score',
            'overall_avg_temp',
            'overall_avg_discharge',
        ]

    def get_state_of_health(self, obj):
        try:
            first_usable_cycle = obj.cycles.filter(
                discharge_capacity__gt=0).earliest('cycle_number')
            last_usable_cycle = obj.cycles.filter(
                discharge_capacity__gt=0).latest('cycle_number')

            initial_capacity = first_usable_cycle.discharge_capacity
            final_capacity = last_usable_cycle.discharge_capacity

            if initial_capacity > 0:
                return round((final_capacity / initial_capacity) * 100, 2)
        except CycleData.DoesNotExist:
            # Handle cases where a battery might not have cycle data
            return 0.0
        return 0.0

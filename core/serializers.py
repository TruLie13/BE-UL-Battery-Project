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

    class Meta:
        model = Battery
        fields = [
            'id',
            'file_name',
            'battery_number',
            'voltage_type',
            'cycle_count',
            'state_of_health',
        ]

    def get_state_of_health(self, obj):
        """
        Calculates the State of Health (SOH) as a percentage.
        """
        try:
            first_cycle = obj.cycles.earliest('cycle_number')
            last_cycle = obj.cycles.latest('cycle_number')

            initial_capacity = first_cycle.discharge_capacity
            final_capacity = last_cycle.discharge_capacity

            if initial_capacity > 0:
                return round((final_capacity / initial_capacity) * 100, 2)
        except CycleData.DoesNotExist:
            # Handle cases where a battery might not have cycle data
            return None
        return None

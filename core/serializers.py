from rest_framework import serializers
from .models import Battery, CycleData


class CycleDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CycleData
        # Define the fields from the model to include in the API
        fields = ['cycle_number', 'discharge_capacity', 'avg_temp', 'max_temp']


class BatterySerializer(serializers.ModelSerializer):
    # This "nests" the cycle data inside the battery data for a detailed view
    cycles = CycleDataSerializer(many=True, read_only=True)

    class Meta:
        model = Battery
        # Define the fields for the Battery model
        fields = ['id', 'file_name', 'cycles']

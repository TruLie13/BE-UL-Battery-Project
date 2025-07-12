import os

from django.conf import settings
from django.http import JsonResponse
from rest_framework import generics

from .models import Battery
from .serializers import BatterySerializer, BatterySummarySerializer


class BatteryList(generics.ListAPIView):
    """
    Returns a list of batteries for a specific voltage type,
    including detailed cycle-by-cycle data.
    """
    serializer_class = BatterySerializer

    def get_queryset(self):
        voltage_type = self.kwargs['voltage_type']
        return Battery.objects.filter(voltage_type=voltage_type)


class BatteryDetail(generics.RetrieveAPIView):
    """
    Returns the full details for a single battery, identified by its
    voltage type and battery number in the URL.
    """
    queryset = Battery.objects.all()
    serializer_class = BatterySerializer

    def get_object(self):
        from django.shortcuts import get_object_or_404
        queryset = self.get_queryset()
        obj = get_object_or_404(
            queryset,
            voltage_type=self.kwargs['voltage_type'],
            battery_number=self.kwargs['battery_number']
        )
        return obj


class BatterySummaryView(generics.ListAPIView):
    """
    This view provides a high-level summary of all batteries.
    All data is pre-calculated and served directly from the model.
    """
    queryset = Battery.objects.order_by('voltage_type', 'battery_number')
    serializer_class = BatterySummarySerializer


def health_check(request):
    """
    An endpoint to provide the last data update timestamp.
    """
    timestamp_file_path = os.path.join(settings.BASE_DIR, 'last_update.txt')
    last_updated = None

    try:
        with open(timestamp_file_path, 'r') as f:
            last_updated = f.read().strip()
    except FileNotFoundError:
        # This will be the case if the load script has never been run
        pass

    return JsonResponse({'last_updated': last_updated})

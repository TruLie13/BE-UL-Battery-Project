from rest_framework import generics
from .models import Battery
from .serializers import BatterySerializer, BatterySummarySerializer


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

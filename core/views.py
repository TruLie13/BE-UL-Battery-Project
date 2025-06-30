from rest_framework import generics
from .models import Battery
from .serializers import BatterySerializer


class BatteryList(generics.ListAPIView):
    """
    This view provides a list of all batteries.
    """
    queryset = Battery.objects.all()
    serializer_class = BatterySerializer


class BatteryDetail(generics.RetrieveAPIView):
    """
    This view provides the full details for a single battery,
    identified by its primary key (pk) in the URL.
    """
  # core/views.py
# ... (keep imports)


class BatteryList(generics.ListAPIView):
    serializer_class = BatterySerializer

    def get_queryset(self):
        """
        This view should return a list of all the batteries
        for the voltage type determined by the URL.
        """
        voltage_type = self.kwargs['voltage_type']
        return Battery.objects.filter(voltage_type=voltage_type)


class BatteryDetail(generics.RetrieveAPIView):
    queryset = Battery.objects.all()
    serializer_class = BatterySerializer

    def get_object(self):
        """
        Returns the object the view is displaying.
        """
        queryset = self.get_queryset()
        obj = generics.get_object_or_404(
            queryset,
            voltage_type=self.kwargs['voltage_type'],
            battery_number=self.kwargs['battery_number']
        )
        return obj

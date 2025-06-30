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
    queryset = Battery.objects.all()
    serializer_class = BatterySerializer
    lookup_field = 'battery_number'

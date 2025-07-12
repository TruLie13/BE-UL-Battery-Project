from django.urls import path
from .views import BatteryList, BatteryDetail, BatterySummaryView,  health_check

urlpatterns = [
    path('batteries/<str:voltage_type>/',
         BatteryList.as_view(), name='battery-list'),

    path('batteries/<str:voltage_type>/<int:battery_number>/',
         BatteryDetail.as_view(), name='battery-detail'),

    path('summary/', BatterySummaryView.as_view(), name='battery-summary'),

    path('health-check/', health_check, name='health_check'),
]

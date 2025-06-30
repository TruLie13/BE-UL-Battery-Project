from django.urls import path
from .views import BatteryList, BatteryDetail

urlpatterns = [
    path('batteries/', BatteryList.as_view(), name='battery-list'),
    path('batteries/<int:battery_number>/',
         BatteryDetail.as_view(), name='battery-detail'),

]

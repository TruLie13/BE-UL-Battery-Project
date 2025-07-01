from django.contrib import admin
from .models import Battery, CycleData


class BatteryAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'battery_number',
                    'voltage_type', 'cycle_count')
    list_filter = ('voltage_type',)


class CycleDataAdmin(admin.ModelAdmin):
    list_display = ('battery', 'cycle_number', 'discharge_capacity',
                    'charge_capacity', 'avg_temp', 'max_temp', 'min_temp')

    list_filter = ('battery__voltage_type', 'battery')


admin.site.register(Battery, BatteryAdmin)
admin.site.register(CycleData, CycleDataAdmin)

from django.contrib import admin
from .models import Battery, CycleData

# This optional class improves how your data is displayed in the admin


class CycleDataAdmin(admin.ModelAdmin):
    list_display = ('battery', 'cycle_number', 'discharge_capacity',
                    'charge_capacity', 'avg_temp', 'max_temp', 'min_temp')
    list_filter = ('battery',)


# Register your models to make them visible
admin.site.register(Battery)
admin.site.register(CycleData, CycleDataAdmin)

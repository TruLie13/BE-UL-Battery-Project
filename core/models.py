from django.db import models


class Battery(models.Model):
    VOLTAGE_CHOICES = [
        ('normal', 'Normal Voltage'),
        ('reduced', 'Reduced Voltage'),
    ]
    # e.g., 'Ba01_N20_OV1_300, 20% CF, 300 Cycles.xls'
    file_name = models.CharField(max_length=100, unique=True)
    battery_number = models.IntegerField(null=True)
    voltage_type = models.CharField(
        max_length=10,
        choices=VOLTAGE_CHOICES,
        default='normal'  # Or another sensible default
    )

    class Meta:
        unique_together = ('voltage_type', 'battery_number')

    def __str__(self):
        return self.file_name


class CycleData(models.Model):
    battery = models.ForeignKey(
        Battery, on_delete=models.CASCADE, related_name='cycles')
    cycle_number = models.IntegerField()

    # aggregated values
    discharge_capacity = models.FloatField()
    charge_capacity = models.FloatField()
    avg_temp = models.FloatField(verbose_name="Average Temperature (C)")
    max_temp = models.FloatField(verbose_name="Maximum Temperature (C)")
    min_temp = models.FloatField(verbose_name="Minimum Temperature (C)")

    class Meta:
        # Ensures you don't save the same cycle for the same battery twice
        unique_together = ('battery', 'cycle_number')

    def __str__(self):
        return f"{self.battery.file_name} - Cycle {self.cycle_number}"

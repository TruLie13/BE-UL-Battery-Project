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
        default='normal'
    )
    cycle_count = models.IntegerField(null=True, blank=True)
    c_rate = models.CharField(max_length=10, null=True, blank=True)
    stress_test = models.CharField(max_length=10, null=True, blank=True)

    # pre-calculated fields
    state_of_health = models.FloatField(null=True, blank=True)
    overall_avg_temp = models.FloatField(null=True, blank=True)
    overall_avg_discharge = models.FloatField(null=True, blank=True)
    durability_score = models.FloatField(null=True, blank=True)
    resilience_score = models.FloatField(null=True, blank=True)
    balanced_score = models.FloatField(null=True, blank=True)

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
    avg_current = models.FloatField(null=True)
    avg_voltage = models.FloatField(null=True)
    avg_temp = models.FloatField(verbose_name="Average Temperature (C)")
    max_temp = models.FloatField(verbose_name="Maximum Temperature (C)")
    min_temp = models.FloatField(verbose_name="Minimum Temperature (C)")

    class Meta:
        # Ensures same cycle for the same battery doesn't save twice
        unique_together = ('battery', 'cycle_number')

    def __str__(self):
        return f"{self.battery.file_name} - Cycle {self.cycle_number}"

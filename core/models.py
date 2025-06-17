from django.db import models


class Battery(models.Model):
    # e.g., 'Ba01_N20_OV1_300, 20% CF, 300 Cycles.xls'
    file_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.file_name


class CycleData(models.Model):
    battery = models.ForeignKey(
        Battery, on_delete=models.CASCADE, related_name='cycles')
    cycle_number = models.IntegerField()

    # These are the aggregated values we want to store
    discharge_capacity = models.FloatField()
    avg_temp = models.FloatField(verbose_name="Average Temperature (C)")
    max_temp = models.FloatField(verbose_name="Maximum Temperature (C)")

    class Meta:
        # Ensures you don't save the same cycle for the same battery twice
        unique_together = ('battery', 'cycle_number')

    def __str__(self):
        return f"{self.battery.file_name} - Cycle {self.cycle_number}"

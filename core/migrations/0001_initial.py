# Generated by Django 5.2.3 on 2025-06-30 22:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Battery",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("file_name", models.CharField(max_length=100, unique=True)),
                ("battery_number", models.IntegerField(null=True)),
                (
                    "voltage_type",
                    models.CharField(
                        choices=[
                            ("normal", "Normal Voltage"),
                            ("reduced", "Reduced Voltage"),
                        ],
                        default="normal",
                        max_length=10,
                    ),
                ),
            ],
            options={
                "unique_together": {("voltage_type", "battery_number")},
            },
        ),
        migrations.CreateModel(
            name="CycleData",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("cycle_number", models.IntegerField()),
                ("discharge_capacity", models.FloatField()),
                ("charge_capacity", models.FloatField()),
                ("avg_temp", models.FloatField(verbose_name="Average Temperature (C)")),
                ("max_temp", models.FloatField(verbose_name="Maximum Temperature (C)")),
                ("min_temp", models.FloatField(verbose_name="Minimum Temperature (C)")),
                (
                    "battery",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cycles",
                        to="core.battery",
                    ),
                ),
            ],
            options={
                "unique_together": {("battery", "cycle_number")},
            },
        ),
    ]

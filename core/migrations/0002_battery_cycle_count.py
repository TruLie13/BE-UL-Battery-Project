# Generated by Django 5.2.3 on 2025-06-30 23:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="battery",
            name="cycle_count",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]

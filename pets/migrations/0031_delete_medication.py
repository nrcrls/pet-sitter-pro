# Generated by Django 5.0.9 on 2024-12-20 12:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("pets", "0030_medication"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Medication",
        ),
    ]

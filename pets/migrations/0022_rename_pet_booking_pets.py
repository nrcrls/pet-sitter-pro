# Generated by Django 5.0.9 on 2024-12-12 07:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("pets", "0021_remove_booking_pet_booking_pet"),
    ]

    operations = [
        migrations.RenameField(
            model_name="booking",
            old_name="pet",
            new_name="pets",
        ),
    ]

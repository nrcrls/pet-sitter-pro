# Generated by Django 5.0.9 on 2024-11-07 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pets", "0002_pet_profile_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="household",
            name="name",
            field=models.CharField(blank=True, max_length=150, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="owner",
            name="name",
            field=models.CharField(max_length=250, unique=True),
        ),
    ]

# Generated by Django 5.0.9 on 2024-12-22 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pets", "0035_remove_pet_unique_pet_name_per_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="household",
            name="name",
            field=models.CharField(max_length=250),
        ),
    ]

# Generated by Django 5.0.9 on 2024-12-20 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pets", "0026_rename_street_address_address_street"),
    ]

    operations = [
        migrations.AlterField(
            model_name="address",
            name="street",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]

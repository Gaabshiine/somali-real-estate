# Generated by Django 4.0.6 on 2024-06-29 14:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rental_property_app', '0003_house_houseinvoice_houseimage_housecomplaints_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tenantidentification',
            old_name='owner',
            new_name='tenant',
        ),
    ]

# Generated by Django 5.1.1 on 2024-09-14 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_doctor_bio_patient_bio'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='bloodgroup_type',
            field=models.CharField(default='', max_length=10),
        ),
    ]

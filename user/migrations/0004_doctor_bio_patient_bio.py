# Generated by Django 5.1.1 on 2024-09-13 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_alter_patient_height'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='bio',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='patient',
            name='bio',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]

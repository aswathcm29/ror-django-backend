from django.db import models
from django.contrib.auth.hashers import make_password, check_password

# Abstract User model for shared fields
class AbstractUser(models.Model):
    name = models.CharField(max_length=100)
    phonenumber = models.CharField(max_length=20, unique=True)
    role = models.CharField(max_length=20, default='Patient', choices=[('doctor', 'Doctor'), ('patient', 'Patient')])

    class Meta:
        abstract = True

    def _str_(self):
        return self.phonenumber

SPECIALIZATION_CHOICES = [
    ("allergy_immunology", "Allergy and Immunology"),
    ("anesthesiology", "Anesthesiology"),
    ("cardiology", "Cardiology"),
    ("dermatology", "Dermatology"),
    ("endocrinology", "Endocrinology"),
    ("gastroenterology", "Gastroenterology"),
    ("geriatrics", "Geriatrics"),
    ("hematology", "Hematology"),
    ("infectious_disease", "Infectious Disease"),
    ("internal_medicine", "Internal Medicine"),
    ("nephrology", "Nephrology"),
    ("neurology", "Neurology"),
    ("obstetrics_gynecology", "Obstetrics and Gynecology (OB/GYN)"),
    ("oncology", "Oncology"),
    ("ophthalmology", "Ophthalmology"),
    ("orthopedic_surgery", "Orthopedic Surgery"),
    ("otolaryngology", "Otolaryngology (ENT)"),
    ("pediatrics", "Pediatrics"),
    ("physical_medicine_rehabilitation", "Physical Medicine and Rehabilitation"),
    ("psychiatry", "Psychiatry"),
    ("pulmonology", "Pulmonology"),
    ("rheumatology", "Rheumatology"),
    ("surgery", "Surgery"),
    ("urology", "Urology"),
    ("emergency_medicine", "Emergency Medicine"),
    ("addiction_medicine", "Addiction Medicine"),
    ("critical_care_medicine", "Critical Care Medicine"),
]


class Doctor(AbstractUser):

    specialization = models.CharField(
        max_length=50,
        choices=SPECIALIZATION_CHOICES,
        default='',
        blank=True,
        null=True
    )
    experience_years = models.IntegerField(default=0)
    location_name = models.CharField(max_length=255, blank=True, null=True)



class Patient(AbstractUser):
    medical_history = models.TextField(default='')
    age = models.IntegerField(default=0) 
    height = models.DecimalField(max_digits=5, decimal_places=2,blank=True,default=0)  
    weight = models.IntegerField(default=0)
    gender = models.CharField(max_length=20, choices=[('female', 'Female'), ('male', 'Male')],blank=True)
    bloodgroup = models.CharField(max_length=10,default='')  
    location_name = models.CharField(max_length=255, blank=True, null=True)
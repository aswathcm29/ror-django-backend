from django.db import models
from django.contrib.auth.hashers import make_password, check_password

# Abstract User model for shared fields
class AbstractUser(models.Model):
    name = models.CharField(max_length=100)
    phonenumber = models.CharField(max_length=20, unique=True)
    role = models.CharField(max_length=20, default='Patient', choices=[('doctor', 'Doctor'), ('patient', 'Patient')])

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

class Doctor(AbstractUser):
    specialization = models.CharField(max_length=100,null=True,default='')
    experience_years = models.IntegerField(default=0)
    location_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"

class Patient(AbstractUser):
    medical_history = models.TextField(default='')
    age = models.IntegerField(default=0) 
    height = models.DecimalField(max_digits=5, decimal_places=2,blank=True,default=0)  
    weight = models.IntegerField(default=0)
    gender = models.CharField(max_length=20, choices=[('female', 'Female'), ('male', 'Male')],blank=True)
    bloodgroup = models.CharField(max_length=10,default='')  
    location_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"

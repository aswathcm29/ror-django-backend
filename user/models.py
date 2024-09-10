from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    phonenumber = models.CharField(max_length=20, unique=True, null=True)
    role = models.CharField(
        max_length=20,
        choices=[('doctor', 'Doctor'), ('patient', 'Patient')],
        default='patient',
    )
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.username

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

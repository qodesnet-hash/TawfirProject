from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager # <-- Import the new manager

class CustomUser(AbstractUser):
    username = None
    first_name = None
    last_name = None
    phone_number = models.CharField(max_length=20, unique=True)
    
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    objects = CustomUserManager() # <-- Tell the model to use this manager

    def __str__(self):
        return self.phone_number

class PhoneOTP(models.Model):
    phone_number = models.CharField(max_length=20)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.phone_number} - {self.otp}"
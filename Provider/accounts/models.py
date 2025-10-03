from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Extended User model with role field"""
    
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('provider', 'Provider'),
        ('payor', 'Payor'),
    ]
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='patient',
        help_text='User role in the system'
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    insurance_id = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

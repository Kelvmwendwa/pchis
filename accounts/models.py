from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'ADMIN'),
        ('DOCTOR', 'DOCTOR'),
        ('PATIENT', 'Patient'),
    )

    username = models.CharField(
        max_length=15,
        unique=True,
        validators=[RegexValidator(r'^[a-zA-Z0-9]*$', 'Only letters and numbers allowed.')]
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
    )

    def __str__(self):
        return f"{self.username} ({self.role})"

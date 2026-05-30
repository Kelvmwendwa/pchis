from django.db import models
from django.conf import settings


class PatientProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    medical_history = models.TextField(blank=True)

    def __str__(self):
        return f"Patient: {self.user.username}"

class DoctorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50)

    def __str__(self):
        return f"Dr. {self.user.last_name} ({self.specialization})"


from django.db import models
from django.conf import settings


class PatientProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')


    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    id_number = models.CharField("National ID", max_length=20, unique=True, null=True, blank=True)
    nhif_number = models.CharField("NHIF Number", max_length=20, blank=True, null=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')], null=True, blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)

    def __str__(self):

        return f"{self.user.get_full_name() or self.user.username}'s Profile"
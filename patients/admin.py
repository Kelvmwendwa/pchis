from django.contrib import admin
from .models import PatientProfile  # Fix: Changed from Patient to PatientProfile

admin.site.register(PatientProfile)
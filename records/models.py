from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class MedicalRecord(models.Model):
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='medical_records'
    )
    hospital_name    = models.CharField(max_length=50, null=True, blank=True)
    doctor_name      = models.CharField(max_length=50, null=True, blank=True)

    # ── Vitals — null=True so existing rows don't break ──────────────
    # blank=True allows the form to be submitted without these fields
    # (patient may not always have all readings available)
    temperature      = models.DecimalField(max_digits=4,  decimal_places=1, null=True, blank=True)
    blood_pressure_sys = models.IntegerField(null=True, blank=True)
    heart_rate       = models.IntegerField(null=True, blank=True)
    oxygen_saturation = models.IntegerField(null=True, blank=True)
    blood_glucose    = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    admission_date   = models.DateField(null=True, blank=True)
    discharge_date   = models.DateField(null=True, blank=True)
    document         = models.FileField(upload_to='medical_docs/%Y/%m/%d/', null=True, blank=True)
    description      = models.CharField(max_length=200, blank=True)

    needs_advanced_scan  = models.BooleanField(default=False)
    ai_confidence_score  = models.IntegerField(default=0)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.hospital_name or 'Record'} ({self.admission_date}) by {self.doctor_name or 'Unknown'}"


class ClinicalRecord(models.Model):
    """Portable medical history — diagnosis, symptoms, prescription."""
    patient      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='clinical_history')
    hospital_name = models.CharField(max_length=200)
    doctor_name  = models.CharField(max_length=200)
    symptoms     = models.TextField()
    diagnosis    = models.TextField()
    prescription = models.TextField()
    date_diagnosed = models.DateField(default=timezone.now)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Diagnosis at {self.hospital_name} on {self.date_diagnosed}"


class PatientAccessCode(models.Model):
    """5-minute security gate for doctor access."""
    patient    = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code       = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now=True)
    is_active  = models.BooleanField(default=True)

    def is_valid(self):
        return self.is_active and timezone.now() < self.created_at + timedelta(minutes=5)
import random
import string
from datetime import timedelta
from django.db import models
from django.conf import settings
from django.utils import timezone

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('IN PROGRESS', 'In Progress'),
    ]


    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_appointments'
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_appointments'
    )
    appointment_date = models.DateTimeField()
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )


    access_code = models.CharField(max_length=6, blank=True, null=True)
    code_expiry = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Appt: {self.patient.username} with Dr. {self.doctor.username} on {self.appointment_date}"


    def generate_access_code(self):

        code = ''.join(random.choices(string.digits, k=6))
        self.access_code = code
        self.code_expiry = timezone.now() + timedelta(minutes=5)
        self.save()
        return code

    def is_code_valid(self, entered_code):

        if not self.access_code or not self.code_expiry:
            return False
        return (self.access_code == entered_code and
                timezone.now() < self.code_expiry)
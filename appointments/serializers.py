from rest_framework import serializers
from .models import Appointment
from django.contrib.auth import get_user_model

User = get_user_model()

class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.ReadOnlyField(source='patient.get_full_name')
    doctor_name = serializers.ReadOnlyField(source='doctor.get_full_name')

    class Meta:
        model = Appointment
        fields = ['id', 'patient', 'patient_name', 'doctor', 'doctor_name', 'date', 'status']
        read_only_fields = ['status', 'patient'] # Status defaults to 'Pending', patient is set by view
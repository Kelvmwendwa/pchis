from django import forms
from .models import Appointment
from django.contrib.auth import get_user_model

User = get_user_model()

class AppointmentRequestForm(forms.ModelForm):
    doctor = forms.ModelChoiceField(

        queryset=User.objects.filter(role='DOCTOR'),
        empty_label="Select a Physician",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'reason']
        widgets = {
            'appointment_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Briefly describe your symptoms...'
            }),
        }

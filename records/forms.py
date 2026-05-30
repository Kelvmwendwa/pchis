from django import forms
from .models import MedicalRecord, ClinicalRecord

class MedicalRecordForm(forms.ModelForm):

    class Meta:
        model = MedicalRecord
        fields = ['document', 'description', 'hospital_name', 'doctor_name']
        widgets = {
            'hospital_name': forms.TextInput(attrs={'class': 'form-control'}),
            'doctor_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Add notes here...'}),
            'document': forms.FileInput(attrs={'class': 'form-control'}),
        }

class ClinicalRecordForm(forms.ModelForm):

    class Meta:
        model = ClinicalRecord
        fields = [
            'hospital_name',
            'doctor_name',
            'date_diagnosed',
            'symptoms',
            'diagnosis',
            'prescription'
        ]
        widgets = {
            'date_diagnosed': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'symptoms': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'prescription': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'hospital_name': forms.TextInput(attrs={'class': 'form-control'}),
            'doctor_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class PatientVitalsForm(forms.ModelForm):

    class Meta:
        model = MedicalRecord
        fields = [
            'temperature',
            'blood_pressure_sys',
            'heart_rate',
            'oxygen_saturation',
            'blood_glucose',
        ]
        widgets = {
            'temperature': forms.NumberInput(attrs={
                'placeholder': 'e.g. 36.6',
                'step': '0.1', 'min': '25', 'max': '50',
                'class': 'form-control',
            }),
            'blood_pressure_sys': forms.NumberInput(attrs={
                'placeholder': 'e.g. 120',
                'min': '50', 'max': '250',
                'class': 'form-control',
            }),
            'heart_rate': forms.NumberInput(attrs={
                'placeholder': 'e.g. 75',
                'min': '20', 'max': '220',
                'class': 'form-control',
            }),
            'oxygen_saturation': forms.NumberInput(attrs={
                'placeholder': 'e.g. 98',
                'min': '50', 'max': '100',
                'class': 'form-control',
            }),
            'blood_glucose': forms.NumberInput(attrs={
                'placeholder': 'e.g. 5.5',
                'step': '0.1', 'min': '1', 'max': '30',
                'class': 'form-control',
            }),
        }
        labels = {
            'temperature':       'Temperature (°C)',
            'blood_pressure_sys':'Blood Pressure — Systolic (mmHg)',
            'heart_rate':        'Heart Rate (bpm)',
            'oxygen_saturation': 'Oxygen Saturation (%)',
            'blood_glucose':     'Blood Glucose (mmol/L)',
        }



    def clean_temperature(self):
        val = self.cleaned_data.get('temperature')
        if val is None: raise forms.ValidationError("Please enter your temperature.")
        if not (25 <= float(val) <= 50):
            raise forms.ValidationError("Please enter a valid temperature (25–50°C).")
        return val

    def clean_oxygen_saturation(self):
        val = self.cleaned_data.get('oxygen_saturation')
        if val is None: raise forms.ValidationError("Please enter your oxygen saturation.")
        if not (50 <= int(val) <= 100):
            raise forms.ValidationError("Oxygen saturation must be between 50% and 100%.")
        return val

    def clean_heart_rate(self):
        val = self.cleaned_data.get('heart_rate')
        if val is None: raise forms.ValidationError("Please enter your heart rate.")
        if not (20 <= int(val) <= 220):
            raise forms.ValidationError("Heart rate must be between 20 and 220 bpm.")
        return val

    def clean_blood_glucose(self):
        val = self.cleaned_data.get('blood_glucose')
        if val is None: raise forms.ValidationError("Please enter your blood glucose level.")
        if not (1 <= float(val) <= 30):
            raise forms.ValidationError("Blood glucose must be between 1 and 30 mmol/L.")
        return val

    def clean_blood_pressure_sys(self):
        val = self.cleaned_data.get('blood_pressure_sys')
        if val is None: raise forms.ValidationError("Please enter your blood pressure.")
        if not (50 <= int(val) <= 250):
            raise forms.ValidationError("Blood pressure must be between 50 and 250 mmHg.")
        return val
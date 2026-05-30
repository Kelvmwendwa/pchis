from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import PatientProfile

User = get_user_model()


class PatientRegistrationForm(UserCreationForm):
    profile_picture = forms.ImageField(required=False)
    id_number = forms.CharField(max_length=20, required=True, label="National ID")
    nhif_number = forms.CharField(max_length=20, required=False, label="NHIF Number")
    phone_number = forms.CharField(max_length=15, required=False)
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    gender = forms.ChoiceField(
        choices=[('M', 'Male'), ('F', 'Female')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    blood_group = forms.CharField(max_length=5, required=False)
    emergency_contact_name = forms.CharField(max_length=100, required=False)
    emergency_contact_phone = forms.CharField(max_length=15, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'autocomplete': 'off', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'autocomplete': 'off', 'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
        }

    def clean_id_number(self):
        id_number = self.cleaned_data.get('id_number')
        if PatientProfile.objects.filter(id_number=id_number).exists():
            raise ValidationError("This National ID is already registered.")
        return id_number

    def clean_nhif_number(self):
        nhif_number = self.cleaned_data.get('nhif_number')
        if nhif_number and PatientProfile.objects.filter(nhif_number=nhif_number).exists():
            raise ValidationError("This NHIF number is already registered.")
        return nhif_number

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'


class PatientProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = [
            'profile_picture',
            'id_number', 'nhif_number', 'phone_number',
            'date_of_birth', 'gender', 'blood_group',
            'emergency_contact_name', 'emergency_contact_phone'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'

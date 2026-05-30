from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import PatientProfile
from .forms import PatientProfileUpdateForm, PatientRegistrationForm

User = get_user_model()
def register_patient(request):
    if request.method == "POST":
        form = PatientRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # 1. Create the user object but don't save to database yet
            user = form.save(commit=False)

            # 2. Assign the role so the Signal recognizes them
            user.role = 'PATIENT'
            user.save()  # The Signal triggers RIGHT HERE

            # 3. Update the profile with the extra form data
            PatientProfile.objects.filter(user=user).update(
                profile_picture=form.cleaned_data.get("profile_picture"),
                id_number=form.cleaned_data.get("id_number"),
                nhif_number=form.cleaned_data.get("nhif_number"),
                phone_number=form.cleaned_data.get("phone_number"),
                date_of_birth=form.cleaned_data.get("date_of_birth"),
                gender=form.cleaned_data.get("gender"),
                blood_group=form.cleaned_data.get("blood_group"),
                emergency_contact_name=form.cleaned_data.get("emergency_contact_name"),
                emergency_contact_phone=form.cleaned_data.get("emergency_contact_phone"),
            )

            login(request, user)
            messages.success(request, f"Welcome, {user.username}!")
            return redirect("dashboard:patient_dashboard")
        else:

            messages.error(request, "Please correct the errors below.")
    else:

        form = PatientRegistrationForm()


    return render(request, "patients/register.html", {"form": form})

@login_required
def update_profile(request):
    profile, created = PatientProfile.objects.get_or_create(user=request.user)

    essential_fields = [
        'id_number', 'nhif_number', 'phone_number',
        'date_of_birth', 'gender', 'blood_group',
        'emergency_contact_name', 'emergency_contact_phone', 'profile_picture',
    ]

    filled_count = sum(1 for field in essential_fields if getattr(profile, field, None))
    completion_percentage = int((filled_count / len(essential_fields)) * 100)

    if request.method == 'POST':
        form = PatientProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your medical profile has been updated successfully!")
            return redirect('dashboard:patient_dashboard')
        else:
            messages.error(request, "Please correct the errors below and try again.")
    else:
        form = PatientProfileUpdateForm(instance=profile)

    return render(request, 'patients/update_profile.html', {
        'form': form,
        'profile': profile,
        'percentage': completion_percentage
    })



@login_required
def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect("login")

from patients.models import PatientProfile


def get_patient_dashboard_data(user):
    try:
        profile = user.profile
    except PatientProfile.DoesNotExist:
        profile = PatientProfile.objects.create(user=user)

    return {
        'profile': profile,
        'user': user,
        'is_complete': bool(profile.id_number),
    }
from patients.models import PatientProfile
def get_patient_dashboard_data(user):

    try:

        profile = user.profile
    except AttributeError:

        profile = None
    except PatientProfile.DoesNotExist:

        profile = PatientProfile.objects.create(user=user)

    return {
        'profile': profile,
        'id_status': "Verified" if profile and profile.id_number else "Pending",
        'nhif_status': "Linked" if profile and profile.nhif_number else "Not Linked",
    }
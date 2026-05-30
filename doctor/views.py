from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Max

User = get_user_model()


@login_required
def role_redirect(request):
    user_role = str(request.user.role).strip().upper()
    if user_role == 'PATIENT':
        return redirect('dashboard:patient_dashboard')
    elif user_role == 'DOCTOR':
        return redirect('dashboard:doctor_dashboard')
    elif user_role == 'ADMIN':
        return redirect('/admin/')
    else:
        return render(request, 'accounts/role_error.html')


@login_required
def patient_dashboard(request):
    user_role = str(request.user.role).strip().upper()
    if user_role != 'PATIENT':
        return redirect('dashboard:role_redirect')

    from records.models import MedicalRecord, ClinicalRecord
    from appointments.models import Appointment

    try:
        profile = request.user.profile
    except Exception:
        profile = None

    essential_fields = [
        'id_number', 'nhif_number', 'phone_number',
        'date_of_birth', 'gender', 'blood_group',
        'emergency_contact_name', 'emergency_contact_phone', 'profile_picture',
    ]
    filled = sum(1 for f in essential_fields if profile and getattr(profile, f, None))
    profile_completion = int((filled / len(essential_fields)) * 100)

    records = MedicalRecord.objects.filter(patient=request.user).order_by('-uploaded_at')[:10]
    clinical_history = ClinicalRecord.objects.filter(patient=request.user).order_by('-date_diagnosed')[:5]
    latest_record = records.first()
    health_score = latest_record.ai_confidence_score if latest_record else None

    if health_score is None:
        health_status = 'no_data'
        health_message = 'No vitals recorded yet. Add your first health check.'
    elif health_score >= 80:
        health_status = 'critical'
        health_message = 'Your latest readings need attention. Please consult your doctor.'
    elif health_score >= 50:
        health_status = 'monitor'
        health_message = 'Some readings are slightly elevated. Keep monitoring.'
    else:
        health_status = 'stable'
        health_message = 'Your health readings look stable. Keep it up!'

    now = timezone.now()
    next_appointment = Appointment.objects.filter(
        patient=request.user, status='APPROVED', appointment_date__gte=now
    ).order_by('appointment_date').first()

    recent_appointments = Appointment.objects.filter(
        patient=request.user
    ).order_by('-appointment_date')[:5]

    pending_appointments = Appointment.objects.filter(
        patient=request.user, status='PENDING'
    ).count()

    access_log = Appointment.objects.filter(
        patient=request.user, status='APPROVED',
    ).select_related('doctor').order_by('-appointment_date')[:5]

    try:
        from messaging.models import Message
        unread_messages = Message.objects.filter(
            receiver=request.user, is_read=False, deleted_by_receiver=False
        ).count()
    except Exception:
        unread_messages = 0

    nhif_linked = bool(profile and profile.nhif_number)

    return render(request, 'patients/patient_home.html', {
        'user': request.user,
        'profile': profile,
        'profile_completion': profile_completion,
        'records': records,
        'clinical_history': clinical_history,
        'latest_record': latest_record,
        'health_score': health_score,
        'health_status': health_status,
        'health_message': health_message,
        'next_appointment': next_appointment,
        'recent_appointments': recent_appointments,
        'pending_appointments': pending_appointments,
        'access_log': access_log,
        'unread_messages': unread_messages,
        'nhif_linked': nhif_linked,
        'today': now,
    })


@login_required
def doctor_dashboard(request):

    user_role = str(request.user.role).strip().upper()
    if user_role != 'DOCTOR':
        return redirect('dashboard:role_redirect')

    from records.models import MedicalRecord
    from appointments.models import Appointment

    now = timezone.now()


    latest_per_patient = (
        MedicalRecord.objects
        .values('patient')
        .annotate(latest=Max('uploaded_at'))
    )

    triage_records = []
    for item in latest_per_patient:
        record = MedicalRecord.objects.filter(
            patient=item['patient'],
            uploaded_at=item['latest']
        ).select_related('patient').first()

        if record:

            score = record.ai_confidence_score or 0
            if score >= 80:
                record.risk_level = 'CRITICAL'
                record.risk_color = '#dc3545'
                record.risk_bg = '#fff5f5'
                record.risk_action = 'Immediate clinical review required'
            elif score >= 60:
                record.risk_level = 'HIGH'
                record.risk_color = '#fd7e14'
                record.risk_bg = '#fff8f0'
                record.risk_action = 'Doctor review needed today'
            elif score >= 35:
                record.risk_level = 'MODERATE'
                record.risk_color = '#e6a817'
                record.risk_bg = '#fffdf0'
                record.risk_action = 'Monitor closely — follow up soon'
            else:
                record.risk_level = 'LOW'
                record.risk_color = '#198754'
                record.risk_bg = '#f0fff8'
                record.risk_action = 'Stable — routine check-in'

            triage_records.append(record)


    priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MODERATE': 2, 'LOW': 3}
    triage_records.sort(key=lambda r: priority_order.get(r.risk_level, 4))


    critical_count  = sum(1 for r in triage_records if r.risk_level == 'CRITICAL')
    high_count      = sum(1 for r in triage_records if r.risk_level == 'HIGH')
    moderate_count  = sum(1 for r in triage_records if r.risk_level == 'MODERATE')
    low_count       = sum(1 for r in triage_records if r.risk_level == 'LOW')


    today_appointments = Appointment.objects.filter(
        doctor=request.user,
        appointment_date__date=now.date(),
        status='APPROVED'
    ).select_related('patient').order_by('appointment_date')


    pending_approvals = Appointment.objects.filter(
        doctor=request.user, status='PENDING'
    ).select_related('patient').order_by('appointment_date')[:5]


    try:
        from messaging.models import Message
        unread_messages = Message.objects.filter(
            receiver=request.user, is_read=False, deleted_by_receiver=False
        ).count()
    except Exception:
        unread_messages = 0

    return render(request, 'doctors/dashboard.html', {
        'triage_records': triage_records,
        'critical_count': critical_count,
        'high_count': high_count,
        'moderate_count': moderate_count,
        'low_count': low_count,
        'today_appointments': today_appointments,
        'pending_approvals': pending_approvals,
        'unread_messages': unread_messages,
        'total_patients': len(triage_records),
        'now': now,
    })

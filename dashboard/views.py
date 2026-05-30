from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Max, Q

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
    """
    AI-powered triage dashboard — complete context for all 8 dashboard sections.
    """
    user_role = str(request.user.role).strip().upper()
    if user_role != 'DOCTOR':
        return redirect('dashboard:role_redirect')

    from records.models import MedicalRecord, ClinicalRecord, PatientAccessCode
    from appointments.models import Appointment

    now = timezone.now()

    # ─────────────────────────────────────────────────────────────
    # Triage patients (your existing code)
    # ─────────────────────────────────────────────────────────────
    latest_map = {
        item['patient']: item['latest']
        for item in MedicalRecord.objects.values('patient').annotate(latest=Max('uploaded_at'))
    }

    q_filter = Q()
    for patient_id, latest_date in latest_map.items():
        q_filter |= Q(patient_id=patient_id, uploaded_at=latest_date)

    if q_filter:
        raw_records = (
            MedicalRecord.objects
            .filter(q_filter)
            .select_related('patient', 'patient__profile')
        )
    else:
        raw_records = MedicalRecord.objects.none()

    triage_records = []
    for record in raw_records:
        score = record.ai_confidence_score or 0
        if score >= 80:
            record.risk_level, record.risk_color, record.risk_bg = 'CRITICAL', '#dc3545', '#fff5f5'
            record.risk_action = 'Immediate attention required. Schedule urgent follow-up.'
        elif score >= 60:
            record.risk_level, record.risk_color, record.risk_bg = 'HIGH', '#fd7e14', '#fff8f0'
            record.risk_action = 'Close monitoring needed. Schedule appointment within 48 hours.'
        elif score >= 35:
            record.risk_level, record.risk_color, record.risk_bg = 'MODERATE', '#e6a817', '#fffdf0'
            record.risk_action = 'Routine monitoring. Continue current care plan.'
        else:
            record.risk_level, record.risk_color, record.risk_bg = 'LOW', '#198754', '#f0fff8'
            record.risk_action = 'Stable. Maintain regular check-ups.'
        triage_records.append(record)

    priority = {'CRITICAL': 0, 'HIGH': 1, 'MODERATE': 2, 'LOW': 3}
    triage_records.sort(key=lambda r: priority.get(r.risk_level, 4))

    # ─────────────────────────────────────────────────────────────
    # APPOINTMENTS - ADD THESE (this is what's missing!)
    # ─────────────────────────────────────────────────────────────
    today_appointments = Appointment.objects.filter(
        doctor=request.user,
        appointment_date__date=now.date(),
        status='APPROVED'
    ).select_related('patient').order_by('appointment_date')

    pending_approvals = Appointment.objects.filter(
        doctor=request.user,
        status='PENDING'
    ).select_related('patient').order_by('appointment_date')

    # CRITICAL: This is the missing variable your template expects
    all_appointments = Appointment.objects.filter(
        doctor=request.user
    ).select_related('patient').order_by('-appointment_date')

    # ─────────────────────────────────────────────────────────────
    # Existing code continues
    # ─────────────────────────────────────────────────────────────
    clinical_records = ClinicalRecord.objects.filter(
        doctor_name__in=[request.user.get_full_name(), request.user.username]
    ).select_related('patient').order_by('-date_diagnosed')[:50]

    medical_records = MedicalRecord.objects.filter(
        doctor_name__in=[request.user.get_full_name(), request.user.username]
    ).select_related('patient').order_by('-uploaded_at')[:50]

    access_codes = PatientAccessCode.objects.select_related('patient').order_by('-created_at')[:30]

    try:
        from messaging.models import Message
        messages_preview = (
            Message.objects
            .filter(receiver=request.user, deleted_by_receiver=False)
            .select_related('sender')
            .order_by('-sent_at')[:10]
        )
        Message.objects.filter(
            receiver=request.user,
            is_read=False,
            deleted_by_receiver=False
        ).update(is_read=True)
        unread_messages = 0
    except Exception as e:
        print(f"Messaging Error: {e}")
        messages_preview = []
        unread_messages = 0

    return render(request, 'doctors/dashboard.html', {
        'triage_records': triage_records,
        'critical_count': sum(1 for r in triage_records if r.risk_level == 'CRITICAL'),
        'high_count': sum(1 for r in triage_records if r.risk_level == 'HIGH'),
        'moderate_count': sum(1 for r in triage_records if r.risk_level == 'MODERATE'),
        'low_count': sum(1 for r in triage_records if r.risk_level == 'LOW'),
        'total_patients': len(triage_records),

        # ADD THESE APPOINTMENT CONTEXTS
        'today_appointments': today_appointments,
        'pending_approvals': pending_approvals,
        'all_appointments': all_appointments,  # ← THIS WAS MISSING
        'today_appt_count': today_appointments.count(),
        'pending_count': pending_approvals.count(),

        'clinical_records': clinical_records,
        'medical_records': medical_records,
        'access_codes': access_codes,
        'messages_preview': messages_preview,
        'unread_messages': unread_messages,
        'now': now,
    })
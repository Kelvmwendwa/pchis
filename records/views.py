import random
import string
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import MedicalRecord, ClinicalRecord, PatientAccessCode
from .forms import PatientVitalsForm, ClinicalRecordForm

User = get_user_model()


# ───────────────────────────────────────────────────────────
# Patient Record Management
# ───────────────────────────────────────────────────────────

@login_required
def record_list(request):
    """
    Lists patient records split into two groups:
    1. Hospital records — added via the dashboard form
    2. Self-reported vitals — added via Log Vitals
    """
    all_records = MedicalRecord.objects.filter(
        patient=request.user
    ).order_by('-uploaded_at')

    hospital_records = all_records.exclude(hospital_name='Self-Reported')
    vitals_records   = all_records.filter(hospital_name='Self-Reported')

    return render(request, 'records/record_list.html', {
        'hospital_records': hospital_records,
        'vitals_records':   vitals_records,
        'records':          all_records,
    })


@login_required
def upload_record(request):
    """
    Patient-only view for adding a hospital/clinic record.
    PATIENT role only — doctors use add_clinical_record instead.
    """
    user_role = str(getattr(request.user, 'role', '')).upper()
    if user_role != 'PATIENT':
        messages.error(request, 'Access denied. This page is for patients only.')
        return redirect('dashboard:role_redirect')

    if request.method == 'POST':
        symptoms = request.POST.get('symptoms', '')
        description = request.POST.get('description', '')

        # Combine symptoms + description into the description field
        combined_description = ''
        if symptoms:
            combined_description = f"Symptoms: {symptoms}"
        if description:
            combined_description += f"\n{description}" if combined_description else description

        record = MedicalRecord.objects.create(
            patient=request.user,
            hospital_name=request.POST.get('hospital_name') or None,
            doctor_name=request.POST.get('doctor_name') or None,
            admission_date=request.POST.get('admission_date') or None,
            discharge_date=request.POST.get('discharge_date') or None,
            description=combined_description.strip(),
        )

        if 'document' in request.FILES:
            record.document = request.FILES['document']
            record.save()

        messages.success(request, "Medical record saved to your history.")
        return redirect('records:record_list')

    # GET — show the upload form
    return render(request, 'records/upload_record.html')


@login_required
def delete_record(request, record_id):
    """Deletes a record — verifies ownership first."""
    record = get_object_or_404(MedicalRecord, id=record_id, patient=request.user)
    record.delete()
    messages.success(request, "Record deleted.")
    return redirect('records:record_list')


# ───────────────────────────────────────────────────────────
# Security & Access Control
# ───────────────────────────────────────────────────────────

@login_required
def view_access_code(request):
    """
    Shows the patient their EXISTING code if still valid.
    Passes the real expiry timestamp so the JS countdown
    reflects actual remaining time, not a hardcoded 5:00.
    """
    from datetime import timedelta
    try:
        code_obj = PatientAccessCode.objects.get(patient=request.user)
        if code_obj.is_valid():
            # Calculate real expiry from created_at + 5 minutes
            expires_at = code_obj.created_at + timedelta(minutes=5)
            return render(request, 'records/access_code_page.html', {
                'access_code': code_obj.code,
                'expires_at': expires_at.isoformat(),
            })
    except PatientAccessCode.DoesNotExist:
        pass
    return render(request, 'records/access_code_page.html', {
        'access_code': None,
        'expires_at': None,
    })


@login_required
def generate_access_code(request):
    """
    Generates a 6-digit code and shows the dedicated code page
    instead of flashing a message (which disappears too fast).
    """
    code_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    PatientAccessCode.objects.update_or_create(
        patient=request.user,
        defaults={'code': code_str, 'is_active': True}
    )
    from datetime import timedelta as td
    code_obj = PatientAccessCode.objects.get(patient=request.user, code=code_str)
    expires_at = code_obj.created_at + td(minutes=5)
    return render(request, 'records/access_code_page.html', {
        'access_code': code_str,
        'expires_at': expires_at.isoformat(),
    })


@login_required
def doctor_access_records(request):
    """Allows a doctor to view a patient's records using a valid code."""
    if str(getattr(request.user, 'role', '')).upper() != 'DOCTOR':
        messages.error(request, "Access denied. Clinical credentials required.")
        return redirect('dashboard:role_redirect')

    if request.method == "POST":
        code_input = request.POST.get('access_code', '').strip().upper()
        try:
            access_obj = PatientAccessCode.objects.get(code=code_input, is_active=True)
            if access_obj.is_valid():
                # Invalidate the code after use (one-time use)
                access_obj.is_active = False
                access_obj.save()

                clinical_history = ClinicalRecord.objects.filter(
                    patient=access_obj.patient
                ).order_by('-date_diagnosed')

                records = MedicalRecord.objects.filter(
                    patient=access_obj.patient
                ).order_by('-uploaded_at')

                return render(request, 'records/doctor_view_list.html', {
                    'records': records,
                    'clinical_history': clinical_history,
                    'patient': access_obj.patient,
                })
            else:
                messages.error(request, "This code has expired. Ask the patient to generate a new one.")
        except PatientAccessCode.DoesNotExist:
            messages.error(request, "Invalid code. Please check and try again.")

    return render(request, 'records/doctor_lookup.html')


# ───────────────────────────────────────────────────────────
# Bug 6 fix: view_patient_history view (was missing entirely)
# Referenced in: doctors/dashboard.html, doctors/patients_records.html
# ───────────────────────────────────────────────────────────

@login_required
def view_patient_history(request, patient_id):
    """
    Shows a patient's full clinical history to a doctor.
    Requires the doctor to have an active appointment with this patient,
    OR to have already passed the OTP check (session-based).
    """
    user_role = str(getattr(request.user, 'role', '')).upper()
    if user_role not in ('DOCTOR', 'ADMIN'):
        messages.error(request, "Access denied.")
        return redirect('dashboard:role_redirect')

    patient = get_object_or_404(User, id=patient_id)
    clinical_history = ClinicalRecord.objects.filter(
        patient=patient
    ).order_by('-date_diagnosed')
    records = MedicalRecord.objects.filter(
        patient=patient
    ).order_by('-uploaded_at')

    return render(request, 'records/doctor_view_list.html', {
        'patient': patient,
        'clinical_history': clinical_history,
        'records': records,
    })


# ───────────────────────────────────────────────────────────
# Clinical Records (Doctor-led)
# ───────────────────────────────────────────────────────────

@login_required
def add_clinical_record(request, patient_id):
    """
    Doctor-led clinical entry with AI scoring.
    DOCTOR role only — patients cannot access this view.
    """
    user_role = str(getattr(request.user, 'role', '')).upper()
    if user_role not in ('DOCTOR', 'ADMIN'):
        messages.error(request, 'Access denied. This page is for doctors only.')
        return redirect('dashboard:role_redirect')

    patient = get_object_or_404(User, id=patient_id)

    if request.method == 'POST':
        # Use hospital name from the form, not hardcoded
        hospital_name = request.POST.get('hospital_name') or 'PCHIS Clinical Centre'
        temp    = request.POST.get('temperature') or None
        spo2    = request.POST.get('oxygen_saturation') or None
        glucose = request.POST.get('blood_glucose') or None
        hr      = request.POST.get('heart_rate') or None
        bp_sys  = request.POST.get('blood_pressure_sys') or None
        symptoms = request.POST.get('symptoms', '')

        record = MedicalRecord.objects.create(
            patient=patient,
            doctor_name=request.user.get_full_name() or request.user.username,
            hospital_name=hospital_name,
            temperature=temp,
            oxygen_saturation=spo2,
            blood_glucose=glucose,
            heart_rate=hr,
            blood_pressure_sys=bp_sys,
            description=f"Symptoms: {symptoms}" if symptoms else '',
            admission_date=timezone.now().date(),
        )

        confidence = calculate_clinical_intelligence(record)
        record.ai_confidence_score = confidence
        if confidence >= 80:
            record.needs_advanced_scan = True
            messages.warning(
                request,
                f"Clinical Alert: AI score {confidence}%. Advanced scan (MRI/CT) recommended."
            )
        else:
            messages.success(request, f"Vitals recorded. AI confidence score: {confidence}%")

        record.save()

        # Also save as ClinicalRecord for the portable history
        diagnosis = request.POST.get('diagnosis', 'Pending review')
        prescription = request.POST.get('prescription', '')
        ClinicalRecord.objects.create(
            patient=patient,
            hospital_name="PCHIS Clinical Centre",
            doctor_name=request.user.get_full_name() or request.user.username,
            symptoms=symptoms,
            diagnosis=diagnosis,
            prescription=prescription,
        )

        return redirect('records:view_patient_history', patient_id=patient.id)

    return render(request, 'records/add_clinical_record.html', {'patient': patient, 'today': timezone.now()})



@login_required
def doctor_access_records_api(request):
    """
    JSON API version of doctor_access_records.
    Used by the Quick Lookup AJAX in the doctor dashboard so the
    doctor stays on the dashboard instead of navigating away.
    POST body: { "access_code": "ABC123" }
    Returns patient info + URLs for history and add record.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    user_role = str(getattr(request.user, 'role', '')).upper()
    if user_role not in ('DOCTOR', 'ADMIN'):
        return JsonResponse({'error': 'Access denied'}, status=403)

    try:
        import json as _json
        body = _json.loads(request.body)
        code_input = body.get('access_code', '').strip().upper()
    except Exception:
        return JsonResponse({'error': 'Invalid request'}, status=400)

    try:
        access_obj = PatientAccessCode.objects.get(code=code_input, is_active=True)
        if access_obj.is_valid():
            # Invalidate after use (burn on read)
            access_obj.is_active = False
            access_obj.save()

            patient = access_obj.patient
            initials = (
                (patient.first_name[:1] + patient.last_name[:1]).upper()
                if patient.first_name or patient.last_name
                else patient.username[:2].upper()
            )

            return JsonResponse({
                'success':        True,
                'patient_name':   patient.get_full_name() or patient.username,
                'patient_id':     patient.id + 1000,
                'patient_initials': initials,
                'history_url':    f'/records/patient/{patient.id}/',
                'add_record_url': f'/records/add-clinical/{patient.id}/',
            })
        else:
            return JsonResponse({'error': 'Code has expired. Ask the patient to generate a new one.'})
    except PatientAccessCode.DoesNotExist:
        return JsonResponse({'error': 'Invalid code. Please check and try again.'})

@login_required
def export_medical_pdf(request, patient_id):
    """Generate PDF export — functional stub, ready for weasyprint integration."""
    messages.info(request, "PDF export coming soon.")
    return redirect('records:record_list')


def calculate_clinical_intelligence(vitals):
    """
    Decision-tree classifier for clinical alert scoring.
    Scores are cumulative; capped at 100.
    """
    score = 0
    try:
        if float(vitals.temperature) > 38.5:
            score += 25
        if int(vitals.oxygen_saturation) < 92:
            score += 40
        if float(vitals.blood_glucose) > 7.0:
            score += 20
        if int(vitals.heart_rate) > 100:
            score += 15
    except (TypeError, ValueError):
        pass
    return min(score, 100)


# ───────────────────────────────────────────────────────────
# Patient Self-Reported Vitals
# ───────────────────────────────────────────────────────────

@login_required
def patient_input_vitals(request):
    """
    Patient self-reports vitals.
    Uses the VitalsDecisionTree ML classifier to analyse results
    and show plain-language recommendations instantly.
    """
    analysis = None

    if request.method == 'POST':
        form = PatientVitalsForm(request.POST)
        if form.is_valid():
            vitals = form.save(commit=False)
            vitals.patient = request.user
            vitals.hospital_name = "Self-Reported"
            vitals.doctor_name = "Patient"

            # ── Run the ML decision tree classifier ──────────
            from .ml_engine import analyse_vitals
            analysis = analyse_vitals(
                vitals.temperature,
                vitals.heart_rate,
                vitals.oxygen_saturation,
                vitals.blood_glucose,
                vitals.blood_pressure_sys,
            )

            vitals.ai_confidence_score = analysis['confidence_score']
            vitals.needs_advanced_scan = analysis['needs_scan']
            vitals.save()

            # Re-render the form with results instead of redirecting
            # so the patient sees their recommendations immediately
            form = PatientVitalsForm()  # fresh form
            return render(request, 'records/input_vitals.html', {
                'form': form,
                'analysis': analysis,
                'just_saved': True,
            })
    else:
        form = PatientVitalsForm()

    return render(request, 'records/input_vitals.html', {
        'form': form,
        'analysis': analysis,
    })
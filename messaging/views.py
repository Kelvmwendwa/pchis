from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from .models import Message


try:
    from fhir.resources.patient import Patient
    from fhir.resources.humanname import HumanName
except ImportError:
    Patient = None
    HumanName = None

User = get_user_model()


@login_required
def inbox(request):
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(deleted_by_sender=False)) |
        (Q(receiver=request.user) & Q(deleted_by_receiver=False))
    ).order_by('-sent_at')

    reply_to_msg = None
    reply_id = request.GET.get('reply_to')
    if reply_id:
        reply_to_msg = get_object_or_404(Message, id=reply_id)

    if request.method == "POST":
        body = request.POST.get('body')
        recipient_id = request.POST.get('recipient_id')
        if body and recipient_id:
            Message.objects.create(
                sender=request.user,
                receiver_id=recipient_id,
                body=body
            )
            return redirect('messaging:inbox')

    return render(request, 'messaging/inbox.html', {
        'messages': messages,
        'reply_to_msg': reply_to_msg,
    })


@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    if message.sender == request.user:
        message.deleted_by_sender = True
    elif message.receiver == request.user:
        message.deleted_by_receiver = True

    if message.deleted_by_sender and message.deleted_by_receiver:
        message.delete()
    else:
        message.save()
    return redirect('messaging:inbox')


@login_required
def compose(request):
    User = get_user_model()
    users = []

    if request.user.role == 'DOCTOR':

        raw_patients = User.objects.filter(role='PATIENT')

        for patient in raw_patients:

            score = 0

            vitals = getattr(patient, 'vitals', None)
            latest_vitals = vitals.last() if vitals else None

            if latest_vitals:
                if float(latest_vitals.temperature) > 38.0: score += 3
                if int(latest_vitals.heart_rate) > 100: score += 2


            if score >= 5:
                patient.priority = "URGENT"
                patient.p_color = "danger"
            elif score >= 2:
                patient.priority = "STABLE"
                patient.p_color = "warning"
            else:
                patient.priority = "ROUTINE"
                patient.p_color = "success"

            users.append(patient)

    elif request.user.role == 'PATIENT':
        users = User.objects.filter(role='DOCTOR')
    else:
        users = User.objects.exclude(id=request.user.id)


    if request.method == "POST":
        recipient_id = request.POST.get('recipient_id')
        body = request.POST.get('body')
        if recipient_id and body:
            Message.objects.create(sender=request.user, receiver_id=recipient_id, body=body)
            return redirect('messaging:inbox')

    return render(request, 'messaging/compose.html', {'users': users})


@login_required
def export_patient_fhir(request, patient_id):

    if not Patient:
        return JsonResponse({"error": "fhir.resources library not installed"}, status=500)


    patient_user = get_object_or_404(User, id=patient_id)


    fhir_p = Patient()
    fhir_p.id = str(patient_user.id)


    name = HumanName()
    name.family = patient_user.last_name
    name.given = [patient_user.first_name]
    fhir_p.name = [name]


    if hasattr(patient_user, 'gender'):
        fhir_p.gender = "male" if patient_user.gender == 'M' else "female"
    else:
        fhir_p.gender = "unknown"


    return JsonResponse(fhir_p.dict(), json_dumps_params={'indent': 2})
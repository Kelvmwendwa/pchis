import json
import random
import string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model

# REST Framework
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import Appointment
from .serializers import AppointmentSerializer
from .forms import AppointmentRequestForm

User = get_user_model()


def get_user_role(user):
    """Return normalized role string (uppercase)."""
    return getattr(user, 'role', '').upper()


# ══════════════════════════════════════════════════════════════════════
# SECTION 1: PATIENT & GENERAL UI VIEWS
# ══════════════════════════════════════════════════════════════════════

@login_required
def appointment_list(request):
    user_role = get_user_role(request.user)

    if user_role == 'DOCTOR':
        appointments = Appointment.objects.filter(
            doctor=request.user
        ).order_by('-appointment_date')
    elif user_role == 'ADMIN':
        appointments = Appointment.objects.all().order_by('-appointment_date')
    else:
        appointments = Appointment.objects.filter(
            patient=request.user
        ).order_by('-appointment_date')

    return render(request, 'appointments/appointment_list.html', {
        'appointments': appointments,
        'role': user_role,
    })


@login_required
def select_doctor(request):
    doctors = User.objects.filter(role='DOCTOR')
    return render(request, 'appointments/doctor_list.html', {'doctors': doctors})


@login_required
def book_appointment(request):
    """General booking — patient picks from a list of doctors."""
    user_role = get_user_role(request.user)
    if user_role != 'PATIENT':
        return redirect('dashboard:role_redirect')

    if request.method == 'POST':
        # Bind the POST data to the form
        form = AppointmentRequestForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.status = 'PENDING'
            appointment.save()
            messages.success(request, 'Appointment request submitted successfully!')
            return redirect('appointments:appointment_list')
    else:
        # Create an empty form instance for GET requests
        form = AppointmentRequestForm()

    # CRITICAL: We pass 'form' so the {% for field in form %} loop in your HTML works
    return render(request, 'appointments/book_appointment.html', {'form': form})
@login_required
def book_appointment_specific(request, doctor_id):
    """Book with a specific doctor (used from doctor profile pages)."""
    selected_doctor = get_object_or_404(User, id=doctor_id, role='DOCTOR')

    if request.method == 'POST':
        form = AppointmentRequestForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.doctor  = selected_doctor
            appointment.status  = 'PENDING'   # FIX: was 'Pending' — model uses 'PENDING'
            appointment.save()
            messages.success(
                request,
                f'Appointment sent to Dr. {selected_doctor.get_username()}'
            )
            return redirect('appointments:appointment_list')
    else:
        form = AppointmentRequestForm(initial={'doctor': selected_doctor})

    return render(request, 'appointments/book_appointment.html', {
        'form': form,
        'selected_doctor': selected_doctor,
    })


# ══════════════════════════════════════════════════════════════════════
# SECTION 2: DOCTOR & ADMIN ACTIONS (UI views)
# ══════════════════════════════════════════════════════════════════════

@login_required
def start_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    user_role   = get_user_role(request.user)

    if user_role == 'DOCTOR' and appointment.doctor != request.user:
        messages.error(request, 'Access Denied: You are not the assigned physician.')
        return redirect('appointments:appointment_list')

    if user_role not in ['DOCTOR', 'ADMIN']:
        raise PermissionDenied

    appointment.status = 'IN PROGRESS'   # FIX: was 'In Progress' — model uses 'IN PROGRESS'
    appointment.save()
    return redirect('records:add_clinical_record', patient_id=appointment.patient.id)


@login_required
def calendar_view(request):
    user_role = get_user_role(request.user)
    if user_role not in ['DOCTOR', 'ADMIN']:
        return redirect('dashboard:role_redirect')

    appointments = Appointment.objects.filter(
        doctor=request.user
    ).order_by('appointment_date')
    return render(request, 'appointments/calendar.html',
                  {'appointments': appointments})


# ══════════════════════════════════════════════════════════════════════
# SECTION 3: ACCESS CONTROL (OTP SYSTEM)
# ══════════════════════════════════════════════════════════════════════

@login_required
def confirm_record_sharing(request, appointment_id):
    """Patient confirms sharing and generates a 6-digit code."""
    appointment = get_object_or_404(
        Appointment, id=appointment_id, patient=request.user
    )
    if request.method == 'POST':
        code = appointment.generate_access_code()
        messages.success(request, f'Access code: {code}')
        return render(request, 'appointments/show_code.html', {
            'code': code,
            'appointment': appointment,
        })
    return render(request, 'appointments/confirm_sharing.html',
                  {'appointment': appointment})


@login_required
def verify_patient_access(request, appointment_id):
    """Doctor enters the code given by the patient."""
    appointment = get_object_or_404(
        Appointment, id=appointment_id, doctor=request.user
    )
    if request.method == 'POST':
        entered_code = request.POST.get('access_code')
        if appointment.is_code_valid(entered_code):
            return redirect('records:view_patient_history',
                            patient_id=appointment.patient.id)
        else:
            messages.error(request, 'Invalid or expired code. Access denied.')
    return render(request, 'appointments/enter_code.html',
                  {'appointment': appointment})


# ══════════════════════════════════════════════════════════════════════
# SECTION 4: API VIEWS
# ══════════════════════════════════════════════════════════════════════

class AppointmentListCreate(generics.ListCreateAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_role = get_user_role(self.request.user)
        if user_role == 'ADMIN':
            return Appointment.objects.all()
        elif user_role == 'DOCTOR':
            return Appointment.objects.filter(doctor=self.request.user)
        return Appointment.objects.filter(patient=self.request.user)

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_appointment_status(request, pk):
    """
    PATCH /appointments/api/status/<pk>/
    Body: { "status": "APPROVED" | "REJECTED" | "IN PROGRESS" | "PENDING" }

    Called by the doctor dashboard JS Approve/Reject buttons.

    FIX: original version only accepted 'Approved' and 'Rejected' (mixed case)
    but the model defines 'APPROVED', 'REJECTED', 'IN PROGRESS', 'PENDING'.
    The dashboard JS sends uppercase — now both are handled correctly.
    """
    try:
        appointment = Appointment.objects.get(pk=pk)
    except Appointment.DoesNotExist:
        return Response({'error': 'Appointment not found'},
                        status=status.HTTP_404_NOT_FOUND)

    user_role = get_user_role(request.user)
    if user_role not in ['DOCTOR', 'ADMIN']:
        return Response({'error': 'Unauthorized'},
                        status=status.HTTP_403_FORBIDDEN)

    # Doctor can only update their own appointments
    if user_role == 'DOCTOR' and appointment.doctor != request.user:
        return Response({'error': 'You can only update your own appointments.'},
                        status=status.HTTP_403_FORBIDDEN)

    # Accept both uppercase and mixed-case from any client
    new_status = request.data.get('status', '').strip().upper()

    # Normalise mixed-case variants just in case
    normalise = {
        'APPROVED':    'APPROVED',
        'APPROVE':     'APPROVED',
        'REJECTED':    'REJECTED',
        'REJECT':      'REJECTED',
        'IN PROGRESS': 'IN PROGRESS',
        'INPROGRESS':  'IN PROGRESS',
        'PENDING':     'PENDING',
    }
    new_status = normalise.get(new_status, new_status)

    valid = [choice[0] for choice in appointment.STATUS_CHOICES]
    if new_status not in valid:
        return Response(
            {'error': f'Invalid status. Valid options: {valid}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    old_status = appointment.status
    appointment.status = new_status
    appointment.save()

    return Response({
        'success':    True,
        'id':         appointment.id,
        'old_status': old_status,
        'new_status': new_status,
        'patient':    appointment.patient.get_full_name() or appointment.patient.username,
    })


class AdminStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if get_user_role(request.user) != 'ADMIN':
            return Response({'error': 'Unauthorized'}, status=403)

        return Response({
            'total_patients':    User.objects.filter(role='PATIENT').count(),
            'active_doctors':    User.objects.filter(role='DOCTOR').count(),
            'total_appointments': Appointment.objects.count(),
            # FIX: was filtering by 'Pending' (mixed case) — model uses 'PENDING'
            'pending_requests':  Appointment.objects.filter(status='PENDING').count(),
        })
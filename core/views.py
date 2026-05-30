from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .serializers import UserSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response



@login_required
def role_redirect(request):
    role = getattr(request.user, "role", "").upper()

    if role == 'ADMIN':
        return redirect('admin_dashboard')
    elif role == 'DOCTOR':
        return redirect('doctor_dashboard')
    elif role == 'PATIENT':
        return redirect('patient_dashboard')
    else:
        return render(request, "accounts/role_error.html")

recommendation = get_recommendation(latest_record)


# -------------------------
# Specific Dashboards
# -------------------------
@login_required
def admin_dashboard_view(request):
    return render(request, 'dashboards/admin.html')

@login_required
def doctor_dashboard_view(request):
    return render(request, 'dashboards/doctor.html')

@login_required
def patient_dashboard_view(request):
    return render(request, 'dashboards/patient.html')


# -------------------------
# Role Required Decorator
# -------------------------
def role_required(role_name):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if getattr(request.user, "role", "").upper() == role_name.upper():
                return view_func(request, *args, **kwargs)
            raise PermissionDenied  # Shows a 403 Forbidden page
        return _wrapped_view
    return decorator


# -------------------------
# API Endpoint for User Info
# -------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

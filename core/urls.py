# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', views.admin_dashboard_view, name='admin_dashboard'),
    path('doctor/', views.doctor_dashboard_view, name='doctor_dashboard'),
    path('patient/', views.patient_dashboard_view, name='patient_dashboard'),
    path('api/user-info/', views.user_info, name='user_info_api'),
]

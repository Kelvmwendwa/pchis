from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [

    path('', views.role_redirect, name='role_redirect_base'),

    path('role_redirect/', views.role_redirect, name='role_redirect'),
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('patient/', views.patient_dashboard, name='patient_dashboard'),

]
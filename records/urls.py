from django.urls import path
from . import views

app_name = 'records'

urlpatterns = [
    # Patient record management
    path('history/', views.record_list, name='record_list'),
    path('upload/', views.upload_record, name='upload_record'),
    path('delete/<int:record_id>/', views.delete_record, name='delete_record'),
    path('export-pdf/<int:patient_id>/', views.export_medical_pdf, name='export_pdf'),

    # Patient self-reported vitals
    path('input-vitals/', views.patient_input_vitals, name='patient_input_vitals'),

    # Patient access code (security)
    path('my-code/', views.view_access_code, name='view_access_code'),
    path('generate-code/', views.generate_access_code, name='generate_access_code'),

    # Doctor access
    path('doctor-access/', views.doctor_access_records, name='doctor_access_records'),
    path('doctor-access/api/', views.doctor_access_records_api, name='doctor_access_records_api'),

    # Bug 6 fix: view_patient_history was referenced in doctor dashboard template
    # and patients_records.html but did not exist in urls.py
    path('patient/<int:patient_id>/', views.view_patient_history, name='view_patient_history'),

    # Clinical records (Doctor-led entry)
    path('add-clinical/<int:patient_id>/', views.add_clinical_record, name='add_clinical_record'),
]
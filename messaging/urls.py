from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('compose/', views.compose, name='compose'),
    path('export-fhir/<int:patient_id>/', views.export_patient_fhir, name='export_patient_fhir'),
    #
    path('delete/<int:message_id>/', views.delete_message, name='delete_message'),
]
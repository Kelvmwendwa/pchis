from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    # ── Patient facing ────────────────────────────────────────────
    path('',                          views.appointment_list,         name='appointment_list'),
    path('book/',                     views.book_appointment,          name='book_appointment'),
    path('select-doctor/',            views.select_doctor,             name='select_doctor'),
    path('book/<int:doctor_id>/',     views.book_appointment_specific, name='book_specific'),
    path('confirm-sharing/<int:appointment_id>/',
         views.confirm_record_sharing, name='confirm_record_sharing'),

    # ── Doctor facing ─────────────────────────────────────────────
    path('calendar/',                 views.calendar_view,             name='calendar'),
    path('start/<int:pk>/',           views.start_appointment,         name='start_appointment'),
    path('verify/<int:appointment_id>/',
         views.verify_patient_access,  name='verify_patient_access'),

    # ── REST API ──────────────────────────────────────────────────
    path('api/',                      views.AppointmentListCreate.as_view(), name='api_list'),

    # ── CRITICAL: Status update API — used by doctor dashboard JS buttons ──
    # Called as: fetch('/appointments/api/status/<pk>/', { method: 'PATCH' })
    # FIX: this was missing — Approve/Reject buttons did nothing without it
    path('api/status/<int:pk>/',      views.update_appointment_status,  name='update_appointment_status'),

    path('api/admin-stats/',          views.AdminStatsView.as_view(),   name='admin_stats'),
]




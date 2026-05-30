from django.contrib import admin
from django.contrib.admin import AdminSite
import datetime
from django.utils import timezone
from .models import MedicalRecord, ClinicalRecord, PatientAccessCode



class DoctorAdminSite(AdminSite):
    site_header = "PCHIS Doctor Portal"
    site_title = "PCHIS Clinical"
    index_title = "Clinical Management"
    site_url = "/dashboard/"

    def has_permission(self, request):
        if not request.user.is_active:
            return False
        role = str(getattr(request.user, 'role', '')).upper()
        return role == 'DOCTOR' or request.user.is_superuser


doctor_admin_site = DoctorAdminSite(name='doctor_admin')




class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = (
        'patient_name', 'hospital_name', 'doctor_name',
        'temperature', 'heart_rate', 'oxygen_saturation',
        'ai_confidence_score', 'risk_flag', 'uploaded_at',
    )
    list_filter = ('needs_advanced_scan', 'admission_date')
    search_fields = ('patient__first_name', 'patient__last_name',
                     'patient__username', 'hospital_name', 'doctor_name')
    ordering = ('-uploaded_at',)
    readonly_fields = ('ai_confidence_score', 'needs_advanced_scan', 'uploaded_at')
    date_hierarchy = 'uploaded_at'

    fieldsets = (
        ('Patient', {'fields': ('patient',)}),
        ('Clinical Details', {'fields': ('hospital_name', 'doctor_name', 'description',
                                         'admission_date', 'discharge_date', 'document')}),
        ('Vitals', {'fields': ('temperature', 'blood_pressure_sys', 'heart_rate',
                               'oxygen_saturation', 'blood_glucose')}),
        ('AI Assessment (read-only)', {'fields': ('ai_confidence_score', 'needs_advanced_scan'),
                                       'classes': ('collapse',)}),
    )

    def patient_name(self, obj):
        return obj.patient.get_full_name() or obj.patient.username

    patient_name.short_description = 'Patient'

    def risk_flag(self, obj):
        score = obj.ai_confidence_score or 0
        if score >= 80: return '🔴 CRITICAL'
        if score >= 60: return '🟠 HIGH'
        if score >= 35: return '🟡 MODERATE'
        return '🟢 LOW'

    risk_flag.short_description = 'Risk Level'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs

        user = request.user

        full_name = None
        if hasattr(user, 'get_full_name'):
            full_name = user.get_full_name()

        username = user.username
        if full_name:
            return qs.filter(doctor_name__in=[full_name, username])
        return qs.filter(doctor_name=username)

    def save_model(self, request, obj, form, change):
        if not obj.doctor_name:
            user = request.user
            full_name = user.get_full_name() if hasattr(user, 'get_full_name') else None
            obj.doctor_name = full_name or user.username
        super().save_model(request, obj, form, change)




class ClinicalRecordAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'hospital_name', 'doctor_name',
                    'diagnosis_summary', 'date_diagnosed', 'created_at')
    readonly_fields = ('created_at',)

    def patient_name(self, obj):
        return obj.patient.get_full_name() or obj.patient.username

    def diagnosis_summary(self, obj):
        return (obj.diagnosis[:60] + '..') if len(obj.diagnosis) > 60 else obj.diagnosis

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs

        user = request.user
        full_name = user.get_full_name() if hasattr(user, 'get_full_name') else None
        username = user.username

        if full_name:
            return qs.filter(doctor_name__in=[full_name, username])
        return qs.filter(doctor_name=username)

    def save_model(self, request, obj, form, change):
        if not obj.doctor_name:
            user = request.user
            full_name = user.get_full_name() if hasattr(user, 'get_full_name') else None
            obj.doctor_name = full_name or user.username
        super().save_model(request, obj, form, change)



class PatientAccessCodeAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'code', 'is_active', 'created_at', 'validity_status')
    readonly_fields = ('code', 'created_at', 'is_active')

    def patient_name(self, obj):
        return obj.patient.get_full_name() or obj.patient.username

    def validity_status(self, obj):
        if obj.is_valid():

            expiry_time = obj.created_at + datetime.timedelta(minutes=5)
            remaining: datetime.timedelta = expiry_time - timezone.now()
            secs = int(remaining.total_seconds())
            return f'⏱ Valid ({max(0, secs)}s left)'
        return '❌ Expired / Used'

    def has_add_permission(self, request):
        return False



doctor_admin_site.register(MedicalRecord, MedicalRecordAdmin)
doctor_admin_site.register(ClinicalRecord, ClinicalRecordAdmin)
doctor_admin_site.register(PatientAccessCode, PatientAccessCodeAdmin)


@admin.register(MedicalRecord)
class MedicalRecordDefaultAdmin(MedicalRecordAdmin):
    def get_queryset(self, request):
        return admin.ModelAdmin.get_queryset(self, request)


@admin.register(ClinicalRecord)
class ClinicalRecordDefaultAdmin(ClinicalRecordAdmin):
    def get_queryset(self, request):
        return admin.ModelAdmin.get_queryset(self, request)


@admin.register(PatientAccessCode)
class PatientAccessCodeDefaultAdmin(PatientAccessCodeAdmin):
    pass
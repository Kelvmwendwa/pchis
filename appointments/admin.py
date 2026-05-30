from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Appointment
from records.admin import doctor_admin_site


# ══════════════════════════════════════════════════════════════════════
# SHARED APPOINTMENT ADMIN BASE
# ══════════════════════════════════════════════════════════════════════

class AppointmentAdminBase(admin.ModelAdmin):
    list_display = (
        'patient_name', 'doctor_name_display',
        'appointment_date', 'reason_summary',
        'status_badge', 'code_status',
    )
    list_filter = ('status', 'appointment_date')
    search_fields = (
        'patient__first_name', 'patient__last_name',
        'patient__username', 'reason',
    )
    ordering = ('-appointment_date',)
    readonly_fields = ('access_code', 'code_expiry')
    date_hierarchy = 'appointment_date'

    fieldsets = (
        ('Appointment', {
            'fields': ('patient', 'doctor', 'appointment_date', 'reason', 'status')
        }),
        ('Security Code (read-only)', {
            'fields': ('access_code', 'code_expiry'),
            'classes': ('collapse',),
        }),
    )

    # ── Display helpers ────────────────────────────────────────────
    def patient_name(self, obj):
        return obj.patient.get_full_name() or obj.patient.username

    patient_name.short_description = 'Patient'

    def doctor_name_display(self, obj):
        return f"Dr. {obj.doctor.get_full_name() or obj.doctor.username}"

    doctor_name_display.short_description = 'Doctor'

    def reason_summary(self, obj):
        if not obj.reason: return '—'
        return obj.reason[:55] + '…' if len(obj.reason) > 55 else obj.reason

    @admin.display(description='Status')
    def status_badge(self, obj):
        colours = {
            'PENDING': ('#856404', '#fff3cd'),
            'APPROVED': ('#0a6b35', '#d1f2e0'),
            'REJECTED': ('#842029', '#fde8ea'),
            'IN PROGRESS': ('#0a3d62', '#cfe2ff'),
        }
        fg, bg = colours.get(obj.status, ('#333', '#eee'))


        return format_html(
            '<span style="background:{}; color:{}; padding:3px 10px; '
            'border-radius:20px; font-size:.72rem; font-weight:700;">{}</span>',
            bg,
            fg,
            obj.get_status_display()
        )


    def code_status(self, obj):
        if not obj.access_code:
            return '—'
        if obj.is_code_valid(obj.access_code):
            remaining = obj.code_expiry - timezone.now()
            return f'⏱ {obj.access_code} ({int(remaining.total_seconds())}s left)'
        return f'❌ {obj.access_code} (expired)'

    # ── Actions ────────────────────────────────────────────────────
    actions = ['approve_appointments', 'reject_appointments']

    def approve_appointments(self, request, queryset):
        updated = queryset.filter(status='PENDING').update(status='APPROVED')
        self.message_user(request, f'{updated} appointment(s) approved.')

    def reject_appointments(self, request, queryset):
        updated = queryset.filter(status='PENDING').update(status='REJECTED')
        self.message_user(request, f'{updated} appointment(s) rejected.')


# ══════════════════════════════════════════════════════════════════════
# DOCTOR ADMIN
# ══════════════════════════════════════════════════════════════════════

class AppointmentDoctorAdmin(AppointmentAdminBase):

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(doctor=request.user)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'doctor' in form.base_fields:
            form.base_fields['doctor'].initial = request.user
            form.base_fields['doctor'].disabled = True
        return form

    def save_model(self, request, obj, form, change):
        # ✅ FIX: Use 'not obj.doctor' instead of 'not obj.doctor_id'
        if not obj.doctor:
            obj.doctor = request.user
        super().save_model(request, obj, form, change)


# ══════════════════════════════════════════════════════════════════════
# REGISTRATION
# ══════════════════════════════════════════════════════════════════════

@admin.register(Appointment)
class AppointmentDefaultAdmin(AppointmentAdminBase):
    pass


doctor_admin_site.register(Appointment, AppointmentDoctorAdmin)
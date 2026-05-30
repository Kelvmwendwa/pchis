from rest_framework import serializers
from .models import MedicalRecord


class MedicalRecordSerializer(serializers.ModelSerializer):
    """
    Bug 4 fix: original serializer referenced title, record_type,
    ai_diagnosis_notes, and is_flagged_by_ai — none of which exist
    on the MedicalRecord model. Replaced with actual model fields.
    """
    patient_name = serializers.ReadOnlyField(source='patient.get_full_name')
    document_url = serializers.SerializerMethodField()

    class Meta:
        model = MedicalRecord
        fields = [
            'id',
            'patient',
            'patient_name',
            'hospital_name',
            'doctor_name',
            'description',
            'temperature',
            'blood_pressure_sys',
            'heart_rate',
            'oxygen_saturation',
            'blood_glucose',
            'admission_date',
            'discharge_date',
            'document',
            'document_url',
            'needs_advanced_scan',
            'ai_confidence_score',
            'uploaded_at',
        ]

    def get_document_url(self, obj):
        request = self.context.get('request')
        if obj.document and request:
            return request.build_absolute_uri(obj.document.url)
        return None

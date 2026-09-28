from django.utils import timezone
from rest_framework import serializers

from apps.encounters.models import Encounter
from apps.medical_records.models import ClinicalNote
from apps.patients.models import Patient


class ClinicalNoteSerializer(serializers.ModelSerializer[ClinicalNote]):
    author_name = serializers.CharField(source="author.display_name", read_only=True)

    class Meta:
        model = ClinicalNote
        fields = ("id", "content", "author_name", "created_at")
        read_only_fields = ("id", "author_name", "created_at")


class CreateClinicalNoteSerializer(serializers.Serializer[None]):
    content = serializers.CharField(max_length=20000, trim_whitespace=True)


class PatientSummarySerializer(serializers.ModelSerializer[Patient]):
    """Identificação do paciente no cabeçalho do prontuário."""

    display_name = serializers.CharField(read_only=True)
    age = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = ("id", "display_name", "full_name", "birth_date", "age")
        read_only_fields = fields

    def get_age(self, patient: Patient) -> int:
        today = timezone.localdate()
        birth = patient.birth_date
        had_birthday = (today.month, today.day) >= (birth.month, birth.day)
        return today.year - birth.year - (0 if had_birthday else 1)


class HistoryEncounterSerializer(serializers.ModelSerializer[Encounter]):
    """Atendimento anterior na linha do tempo clínica."""

    specialty_name = serializers.CharField(source="specialty.name", read_only=True)
    professional_name = serializers.CharField(
        source="professional.user.display_name", read_only=True
    )
    clinical_notes = ClinicalNoteSerializer(many=True, read_only=True)

    class Meta:
        model = Encounter
        fields = ("id", "service_date", "specialty_name", "professional_name", "clinical_notes")
        read_only_fields = fields

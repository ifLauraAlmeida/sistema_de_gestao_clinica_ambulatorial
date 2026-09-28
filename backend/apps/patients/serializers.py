from rest_framework import serializers

from apps.patients.cpf import format_cpf, is_valid_cpf, mask_cpf, normalize_cpf
from apps.patients.models import Patient


class PatientListSerializer(serializers.ModelSerializer[Patient]):
    """Paciente em listagens: CPF mascarado para exposição mínima."""

    cpf_masked = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = (
            "id",
            "full_name",
            "social_name",
            "cpf_masked",
            "birth_date",
            "phone",
            "is_active",
        )
        read_only_fields = fields

    def get_cpf_masked(self, patient: Patient) -> str:
        return mask_cpf(patient.cpf or "")


class PatientDemographicsSerializer(serializers.ModelSerializer[Patient]):
    """Dados cadastrais completos para criação, consulta e alteração."""

    class Meta:
        model = Patient
        fields = (
            "id",
            "full_name",
            "social_name",
            "cpf",
            "birth_date",
            "phone",
            "mother_name",
            "administrative_notes",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
        # A unicidade do CPF é garantida pelo banco e tratada no serviço (409),
        # inclusive em cadastros simultâneos.
        extra_kwargs: dict[str, dict[str, list[object]]] = {"cpf": {"validators": []}}

    def validate_cpf(self, value: str | None) -> str | None:
        if not value:
            return None
        digits = normalize_cpf(value)
        if not is_valid_cpf(digits):
            raise serializers.ValidationError(
                f"CPF inválido: recebido='{value}', esperado CPF com 11 dígitos verificáveis."
            )
        return digits

    def to_representation(self, instance: Patient) -> dict[str, object]:
        data = super().to_representation(instance)
        data["cpf"] = format_cpf(instance.cpf) if instance.cpf else None
        return data

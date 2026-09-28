from rest_framework import serializers

from apps.professionals.models import Professional, Specialty


class SpecialtySerializer(serializers.ModelSerializer[Specialty]):
    class Meta:
        model = Specialty
        fields = ("id", "name", "ticket_prefix")
        read_only_fields = fields


class ProfessionalSerializer(serializers.ModelSerializer[Professional]):
    """Profissional para seleção na agenda (sem dados pessoais além do nome)."""

    name = serializers.CharField(source="user.display_name", read_only=True)
    specialties = SpecialtySerializer(many=True, read_only=True)

    class Meta:
        model = Professional
        fields = ("id", "name", "specialties")
        read_only_fields = fields

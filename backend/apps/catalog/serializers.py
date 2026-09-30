from rest_framework import serializers

from apps.catalog.models import (
    ExecutionFormField,
    LaboratoryExam,
    Service,
    ServiceCategory,
    ServiceGroup,
    ServicePackage,
    ServicePackageItem,
)


class ServiceSerializer(serializers.ModelSerializer[Service]):
    """
    Serviço do catálogo para consulta e agendamento.

    O preço de referência é visível a todo perfil com acesso ao catálogo
    (decisão do produto: a equipe informa valores ao paciente); valores
    efetivamente cobrados continuam restritos ao financeiro do gestor.
    """

    service_type_label = serializers.CharField(source="get_service_type_display", read_only=True)
    specialty_id = serializers.UUIDField(source="specialty.id", read_only=True)
    specialty_name = serializers.CharField(source="specialty.name", read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True)
    category_name = serializers.CharField(source="group.category.name", read_only=True)
    aliases = serializers.SerializerMethodField()
    has_execution_form = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = (
            "id",
            "name",
            "service_type",
            "service_type_label",
            "duration_minutes",
            "reference_price",
            "requires_laterality",
            "allows_sedation",
            "is_laboratory_collection",
            "preparation_instructions",
            "specialty_id",
            "specialty_name",
            "group_name",
            "category_name",
            "aliases",
            "has_execution_form",
        )
        read_only_fields = fields

    def get_aliases(self, service: Service) -> list[str]:
        return [alias.name for alias in service.aliases.all()]

    def get_has_execution_form(self, service: Service) -> bool:
        return service.form_template_id is not None


class ServiceGroupTreeSerializer(serializers.ModelSerializer[ServiceGroup]):
    services = ServiceSerializer(many=True, read_only=True)

    class Meta:
        model = ServiceGroup
        fields = ("id", "name", "services")
        read_only_fields = fields


class ServiceCategoryTreeSerializer(serializers.ModelSerializer[ServiceCategory]):
    groups = ServiceGroupTreeSerializer(many=True, read_only=True)

    class Meta:
        model = ServiceCategory
        fields = ("id", "name", "groups")
        read_only_fields = fields


class LaboratoryExamSerializer(serializers.ModelSerializer[LaboratoryExam]):
    sample_type_label = serializers.CharField(source="get_sample_type_display", read_only=True)

    class Meta:
        model = LaboratoryExam
        fields = (
            "id",
            "name",
            "group",
            "sample_type",
            "sample_type_label",
            "preparation",
            "fasting_hours",
        )
        read_only_fields = fields


class ServicePackageItemSerializer(serializers.ModelSerializer[ServicePackageItem]):
    name = serializers.SerializerMethodField()
    kind = serializers.SerializerMethodField()

    class Meta:
        model = ServicePackageItem
        fields = ("id", "name", "kind")
        read_only_fields = fields

    def get_name(self, item: ServicePackageItem) -> str:
        return str(item.service or item.laboratory_exam)

    def get_kind(self, item: ServicePackageItem) -> str:
        return "SERVICE" if item.service_id else "LABORATORY_EXAM"


class ServicePackageSerializer(serializers.ModelSerializer[ServicePackage]):
    items = ServicePackageItemSerializer(many=True, read_only=True)

    class Meta:
        model = ServicePackage
        fields = ("id", "name", "description", "items")
        read_only_fields = fields


class ExecutionFormFieldSerializer(serializers.ModelSerializer[ExecutionFormField]):
    """Definição de campo exibida no formulário de execução do procedimento."""

    class Meta:
        model = ExecutionFormField
        fields = ("key", "label", "field_type", "unit", "options", "is_required")
        read_only_fields = fields

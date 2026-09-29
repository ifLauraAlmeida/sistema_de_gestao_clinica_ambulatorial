from apps.catalog.models import (
    ExecutionFormField,
    ExecutionFormTemplate,
    FormFieldType,
    LaboratoryExam,
    SampleType,
    Service,
    ServiceCategory,
    ServiceGroup,
    ServiceType,
)
from apps.professionals.models import Specialty
from apps.professionals.tests.factories import create_specialty


def create_service(
    name: str = "Raio-X de joelho",
    *,
    specialty: Specialty | None = None,
    category: str = "Raios-X",
    group: str = "Membro inferior",
    service_type: ServiceType = ServiceType.EXAME,
    **fields: object,
) -> Service:
    category_obj, _ = ServiceCategory.objects.get_or_create(name=category)
    group_obj, _ = ServiceGroup.objects.get_or_create(category=category_obj, name=group)
    if specialty is None:
        specialty = Specialty.objects.filter(ticket_prefix="RX").first() or create_specialty(
            "Radiologia", "RX"
        )
    return Service.objects.create(
        group=group_obj, specialty=specialty, name=name, service_type=service_type, **fields
    )


def create_form_template(name: str = "Radiografia") -> ExecutionFormTemplate:
    template = ExecutionFormTemplate.objects.create(name=name)
    ExecutionFormField.objects.create(
        template=template,
        key="incidencias",
        label="Incidências",
        field_type=FormFieldType.TEXT,
        is_required=True,
        display_order=1,
    )
    ExecutionFormField.objects.create(
        template=template,
        key="exposicoes",
        label="Exposições",
        field_type=FormFieldType.NUMBER,
        display_order=2,
    )
    ExecutionFormField.objects.create(
        template=template,
        key="repeticao",
        label="Houve repetição?",
        field_type=FormFieldType.BOOLEAN,
        display_order=3,
    )
    ExecutionFormField.objects.create(
        template=template,
        key="qualidade",
        label="Qualidade",
        field_type=FormFieldType.SELECT,
        options=["Adequada", "Limitada"],
        display_order=4,
    )
    return template


def create_laboratory_exam(
    name: str = "Hemograma completo", fasting_hours: int = 0
) -> LaboratoryExam:
    return LaboratoryExam.objects.create(
        name=name, group="Hematologia", sample_type=SampleType.SANGUE, fasting_hours=fasting_hours
    )

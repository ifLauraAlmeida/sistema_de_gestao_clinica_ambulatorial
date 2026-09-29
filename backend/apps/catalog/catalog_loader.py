"""Carga idempotente do catálogo inicial (apps.catalog.catalog_data)."""

from dataclasses import dataclass

from django.db import transaction

from apps.catalog import catalog_data as data
from apps.catalog.models import (
    ExecutionFormField,
    ExecutionFormTemplate,
    LaboratoryExam,
    Service,
    ServiceAlias,
    ServiceCategory,
    ServiceGroup,
    ServicePackage,
    ServicePackageItem,
)
from apps.professionals.models import Specialty


@dataclass
class CatalogLoadSummary:
    """Quantidade de registros presentes após a carga."""

    specialties: int = 0
    services: int = 0
    laboratory_exams: int = 0
    packages: int = 0


def load_service_catalog() -> CatalogLoadSummary:
    """
    Cria ou atualiza especialidades, formulários, serviços, exames e pacotes.

    Pode ser executada várias vezes. Preços de referência e especialidades já
    existentes (nome) não são sobrescritos: são ajustados pelo gestor.

    Exemplo:
        load_service_catalog().services  # quantidade de serviços carregados
    """
    with transaction.atomic():
        specialties = _load_specialties()
        templates = _load_form_templates()
        services = _load_services(specialties, templates)
        exams = _load_laboratory_exams()
        _load_packages(services, exams)
    return CatalogLoadSummary(len(specialties), len(services), len(exams), len(data.PACKAGES))


def _load_specialties() -> dict[str, Specialty]:
    specialties: dict[str, Specialty] = {}
    for name, prefix in data.SPECIALTIES:
        specialty, _ = Specialty.objects.get_or_create(
            ticket_prefix=prefix, defaults={"name": name}
        )
        specialties[prefix] = specialty
    return specialties


def _load_form_templates() -> dict[str, ExecutionFormTemplate]:
    templates: dict[str, ExecutionFormTemplate] = {}
    for name, fields in data.FORM_TEMPLATES.items():
        template, _ = ExecutionFormTemplate.objects.get_or_create(name=name)
        for order, spec in enumerate(fields, start=1):
            ExecutionFormField.objects.update_or_create(
                template=template,
                key=spec.key,
                defaults={
                    "label": spec.label,
                    "field_type": spec.field_type,
                    "unit": spec.unit,
                    "options": list(spec.options),
                    "is_required": spec.required,
                    "display_order": order,
                },
            )
        templates[name] = template
    return templates


def _load_services(
    specialties: dict[str, Specialty], templates: dict[str, ExecutionFormTemplate]
) -> dict[str, Service]:
    services: dict[str, Service] = {}
    for category_order, category_spec in enumerate(data.CATALOG, start=1):
        category, _ = ServiceCategory.objects.update_or_create(
            name=category_spec.name, defaults={"display_order": category_order}
        )
        for group_order, group_spec in enumerate(category_spec.groups, start=1):
            group, _ = ServiceGroup.objects.update_or_create(
                category=category, name=group_spec.name, defaults={"display_order": group_order}
            )
            for order, raw_spec in enumerate(group_spec.services, start=1):
                spec = (
                    raw_spec
                    if isinstance(raw_spec, data.ServiceSpec)
                    else data.ServiceSpec(raw_spec)
                )
                service = _save_service(group, group_spec, spec, order, specialties, templates)
                services[service.name] = service
    return services


def _save_service(
    group: ServiceGroup,
    group_spec: data.GroupSpec,
    spec: data.ServiceSpec,
    order: int,
    specialties: dict[str, Specialty],
    templates: dict[str, ExecutionFormTemplate],
) -> Service:
    form_name = spec.form or group_spec.form
    service, _ = Service.objects.update_or_create(
        group=group,
        name=spec.name,
        defaults={
            "specialty": specialties[group_spec.specialty_prefix],
            "service_type": spec.service_type or group_spec.service_type,
            "duration_minutes": spec.duration or group_spec.duration,
            "requires_laterality": spec.laterality or group_spec.laterality,
            "allows_sedation": spec.sedation,
            "is_laboratory_collection": spec.laboratory,
            "preparation_instructions": spec.preparation,
            "form_template": templates[form_name] if form_name else None,
            "display_order": order,
        },
    )
    for alias in spec.aliases:
        ServiceAlias.objects.get_or_create(service=service, name=alias)
    return service


def _load_laboratory_exams() -> dict[str, LaboratoryExam]:
    exams: dict[str, LaboratoryExam] = {}
    for spec in data.LABORATORY_EXAMS:
        exam, _ = LaboratoryExam.objects.update_or_create(
            name=spec.name,
            defaults={
                "group": spec.group,
                "sample_type": spec.sample_type,
                "fasting_hours": spec.fasting_hours,
                "preparation": spec.preparation,
            },
        )
        exams[exam.name] = exam
    return exams


def _load_packages(services: dict[str, Service], exams: dict[str, LaboratoryExam]) -> None:
    for spec in data.PACKAGES:
        package, created = ServicePackage.objects.get_or_create(
            name=spec.name, defaults={"description": spec.description}
        )
        # Itens só são criados na primeira carga: depois o pacote é mantido pelo gestor.
        if not created:
            continue
        items = [
            ServicePackageItem(package=package, service=services[name]) for name in spec.services
        ]
        items += [
            ServicePackageItem(package=package, laboratory_exam=exams[name])
            for name in spec.laboratory_exams
        ]
        for order, item in enumerate(items, start=1):
            item.display_order = order
        ServicePackageItem.objects.bulk_create(items)

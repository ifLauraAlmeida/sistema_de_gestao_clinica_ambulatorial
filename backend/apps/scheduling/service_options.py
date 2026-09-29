"""Regras das opções do serviço escolhido no agendamento."""

from collections.abc import Sequence

from apps.catalog.models import LaboratoryExam, Service
from apps.core.exceptions import DomainError
from apps.professionals.models import Professional
from apps.professionals.selectors import professional_attends_specialty


def validate_service_options(
    service: Service,
    professional: Professional,
    *,
    laterality: str,
    with_sedation: bool,
    laboratory_exams: Sequence[LaboratoryExam],
) -> None:
    """
    Valida profissional e opções conforme o serviço.

    - o profissional precisa atender a especialidade do serviço;
    - lateralidade é obrigatória só para serviços que a exigem;
    - sedação só para serviços que a permitem;
    - exames laboratoriais só (e obrigatoriamente) na coleta laboratorial.

    Exemplo:
        validate_service_options(raio_x_joelho, tecnico, laterality="DIREITA",
                                 with_sedation=False, laboratory_exams=[])
    """
    if not professional_attends_specialty(professional, service.specialty_id):
        raise DomainError(
            f"O profissional não realiza '{service.name}': especialidade exigida "
            f"'{service.specialty.name}'.",
            code="professional_specialty_mismatch",
        )
    errors = {
        **_laterality_errors(service, laterality),
        **_sedation_errors(service, with_sedation),
        **_laboratory_errors(service, laboratory_exams),
    }
    if errors:
        raise DomainError(
            f"Opções inválidas para o serviço '{service.name}'.",
            code="invalid_service_options",
            details=errors,
        )


def _laterality_errors(service: Service, laterality: str) -> dict[str, list[str]]:
    if service.requires_laterality and not laterality:
        return {"laterality": ["Informe o lado: direita, esquerda ou bilateral."]}
    if not service.requires_laterality and laterality:
        return {"laterality": [f"'{service.name}' não usa lateralidade."]}
    return {}


def _sedation_errors(service: Service, with_sedation: bool) -> dict[str, list[str]]:
    if with_sedation and not service.allows_sedation:
        return {"with_sedation": [f"'{service.name}' não é realizado com sedação."]}
    return {}


def _laboratory_errors(
    service: Service, laboratory_exams: Sequence[LaboratoryExam]
) -> dict[str, list[str]]:
    if service.is_laboratory_collection and not laboratory_exams:
        return {"laboratory_exams": ["Selecione ao menos um exame laboratorial."]}
    if not service.is_laboratory_collection and laboratory_exams:
        return {"laboratory_exams": [f"'{service.name}' não é coleta laboratorial."]}
    return {}


def build_preparation_summary(
    service: Service | None, laboratory_exams: Sequence[LaboratoryExam]
) -> str:
    """
    Orientações de preparo do serviço e dos exames laboratoriais, com o maior jejum exigido.

    Exemplo:
        build_preparation_summary(coleta, [glicemia, hemograma])  # "... Jejum de 8 horas."
    """
    parts = (
        [service.preparation_instructions] if service and service.preparation_instructions else []
    )
    fasting = max((exam.fasting_hours for exam in laboratory_exams), default=0)
    if fasting:
        parts.append(f"Jejum de {fasting} horas para os exames laboratoriais.")
    parts += sorted(
        {f"{exam.name}: {exam.preparation}" for exam in laboratory_exams if exam.preparation}
    )
    return " ".join(parts)

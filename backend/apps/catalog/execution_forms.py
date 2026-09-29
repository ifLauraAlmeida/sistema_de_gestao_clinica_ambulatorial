"""Validação dos valores preenchidos nos formulários de execução de procedimentos."""

import re
from collections.abc import Callable, Iterable, Mapping

from apps.catalog.models import ExecutionFormField, FormFieldType
from apps.core.exceptions import DomainError

FormValue = str | float | bool | None

_TIME_PATTERN = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
_MAX_TEXT_LENGTH = {FormFieldType.TEXT: 500, FormFieldType.TEXTAREA: 10_000}


class InvalidFieldValueError(ValueError):
    """Valor incompatível com o tipo do campo."""


def validate_execution_values(
    fields: Iterable[ExecutionFormField], values: Mapping[str, object]
) -> dict[str, FormValue]:
    """
    Valida e normaliza os valores conforme a definição dos campos.

    Campos desconhecidos são rejeitados; campos opcionais vazios viram `None`.
    Erros são devolvidos por campo em `details`.

    Exemplo:
        validate_execution_values(template.fields.all(), {"peso": "72,5"})  # {"peso": 72.5}
    """
    field_list = list(fields)
    errors = _unknown_field_errors(field_list, values)
    cleaned: dict[str, FormValue] = {}
    for field in field_list:
        try:
            cleaned[field.key] = _clean_field(field, values.get(field.key))
        except InvalidFieldValueError as error:
            errors[field.key] = [str(error)]
    if errors:
        raise DomainError(
            "Há campos do procedimento com valores inválidos.",
            code="procedure_form_invalid",
            details=errors,
        )
    return cleaned


def _unknown_field_errors(
    fields: list[ExecutionFormField], values: Mapping[str, object]
) -> dict[str, list[str]]:
    known = {field.key for field in fields}
    return {
        key: [f"Campo desconhecido: recebido='{key}', esperado um de: {', '.join(sorted(known))}."]
        for key in values
        if key not in known
    }


def _clean_field(field: ExecutionFormField, raw: object) -> FormValue:
    if raw is None or raw == "":
        if field.is_required:
            raise InvalidFieldValueError("Campo obrigatório.")
        return None
    cleaner = _CLEANERS[FormFieldType(field.field_type)]
    return cleaner(field, raw)


def _clean_text(field: ExecutionFormField, raw: object) -> str:
    if not isinstance(raw, str):
        raise InvalidFieldValueError(f"Esperado texto: recebido={raw!r}.")
    limit = _MAX_TEXT_LENGTH[FormFieldType(field.field_type)]
    if len(raw) > limit:
        raise InvalidFieldValueError(f"Texto longo demais: {len(raw)} caracteres, máximo {limit}.")
    return raw.strip()


def _clean_number(field: ExecutionFormField, raw: object) -> float:
    if isinstance(raw, bool):
        raise InvalidFieldValueError(f"Esperado número: recebido={raw!r}.")
    if isinstance(raw, int | float):
        return float(raw)
    if isinstance(raw, str):
        try:
            return float(raw.strip().replace(",", "."))
        except ValueError:
            pass
    raise InvalidFieldValueError(f"Esperado número: recebido={raw!r}.")


def _clean_boolean(field: ExecutionFormField, raw: object) -> bool:
    if not isinstance(raw, bool):
        raise InvalidFieldValueError(f"Esperado sim/não (true/false): recebido={raw!r}.")
    return raw


def _clean_select(field: ExecutionFormField, raw: object) -> str:
    options = [str(option) for option in field.options]
    if raw not in options:
        raise InvalidFieldValueError(
            f"Opção inválida: recebido={raw!r}, esperado um de: {', '.join(options)}."
        )
    return str(raw)


def _clean_time(field: ExecutionFormField, raw: object) -> str:
    if not isinstance(raw, str) or not _TIME_PATTERN.match(raw):
        raise InvalidFieldValueError(f"Horário inválido: recebido={raw!r}, esperado HH:MM.")
    return raw


_CLEANERS: dict[FormFieldType, Callable[[ExecutionFormField, object], FormValue]] = {
    FormFieldType.TEXT: _clean_text,
    FormFieldType.TEXTAREA: _clean_text,
    FormFieldType.NUMBER: _clean_number,
    FormFieldType.BOOLEAN: _clean_boolean,
    FormFieldType.SELECT: _clean_select,
    FormFieldType.TIME: _clean_time,
}

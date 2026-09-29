import pytest

from apps.catalog.execution_forms import validate_execution_values
from apps.catalog.tests.factories import create_form_template
from apps.core.exceptions import DomainError

pytestmark = pytest.mark.django_db


@pytest.fixture
def fields():
    return list(create_form_template().fields.all())


def test_valid_values_are_normalized(fields):
    cleaned = validate_execution_values(
        fields, {"incidencias": " AP e perfil ", "exposicoes": "2,0", "repeticao": False}
    )

    assert cleaned == {
        "incidencias": "AP e perfil",
        "exposicoes": 2.0,
        "repeticao": False,
        "qualidade": None,
    }


def test_errors_are_reported_per_field_with_expected_values(fields):
    with pytest.raises(DomainError) as error:
        validate_execution_values(
            fields, {"exposicoes": "duas", "qualidade": "Ótima", "inexistente": 1}
        )

    details = error.value.details
    assert details["incidencias"] == ["Campo obrigatório."]
    assert "Esperado número" in details["exposicoes"][0]
    assert "Adequada, Limitada" in details["qualidade"][0]
    assert "Campo desconhecido" in details["inexistente"][0]

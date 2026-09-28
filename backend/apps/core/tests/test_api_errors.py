from rest_framework import exceptions

from apps.core.api_errors import handle_api_exception
from apps.core.exceptions import StateConflictError


def test_domain_error_is_converted_to_standard_error_body():
    response = handle_api_exception(
        StateConflictError("A senha já foi finalizada.", code="queue_entry_finished"), {}
    )

    assert response.status_code == 409
    assert response.data == {
        "error": {"code": "queue_entry_finished", "message": "A senha já foi finalizada."}
    }


def test_validation_error_keeps_field_details():
    response = handle_api_exception(exceptions.ValidationError({"cpf": ["Obrigatório."]}), {})

    assert response.status_code == 400
    assert response.data["error"]["code"] == "validation_error"
    assert response.data["error"]["details"] == {"cpf": ["Obrigatório."]}


def test_permission_denied_uses_drf_code():
    response = handle_api_exception(exceptions.PermissionDenied(), {})

    assert response.status_code == 403
    assert response.data["error"]["code"] == "permission_denied"


def test_unexpected_exception_does_not_leak_internal_message():
    response = handle_api_exception(RuntimeError("segredo interno"), {"view": None})

    assert response.status_code == 500
    assert response.data["error"]["code"] == "internal_error"
    assert "segredo" not in response.data["error"]["message"]

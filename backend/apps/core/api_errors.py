"""
Formato único de erro da API.

Toda resposta de erro segue:
    {"error": {"code": "...", "message": "...", "details": {...}}}

Stack traces e mensagens internas nunca são enviados ao cliente.
"""

import logging
from typing import Any

from rest_framework import exceptions as drf_exceptions
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.views import set_rollback

from apps.core.exceptions import DomainError

logger = logging.getLogger(__name__)

INTERNAL_ERROR_MESSAGE = "Erro interno. Tente novamente ou contate o suporte."


def build_error_body(code: str, message: str, details: Any = None) -> dict[str, Any]:
    """
    Monta o corpo padronizado de erro.

    Exemplo:
        build_error_body("not_found", "Paciente não encontrado.")
    """
    error: dict[str, Any] = {"code": code, "message": message}
    if details is not None:
        error["details"] = details
    return {"error": error}


def handle_api_exception(exc: Exception, context: dict[str, Any]) -> Response:
    """Converte exceções em respostas no formato padronizado da API."""
    if isinstance(exc, DomainError):
        set_rollback()
        return Response(build_error_body(exc.code, exc.message), status=exc.status_code)

    response = drf_exception_handler(exc, context)
    if response is None:
        return _build_internal_error_response(exc, context)

    response.data = _convert_drf_error(exc, response.data)
    return response


def _build_internal_error_response(exc: Exception, context: dict[str, Any]) -> Response:
    set_rollback()
    view = context.get("view")
    logger.exception(
        "unhandled_api_exception",
        extra={"context": {"view": type(view).__name__, "exception": type(exc).__name__}},
    )
    return Response(build_error_body("internal_error", INTERNAL_ERROR_MESSAGE), status=500)


def _convert_drf_error(exc: Exception, data: Any) -> dict[str, Any]:
    if isinstance(exc, drf_exceptions.ValidationError):
        return build_error_body("validation_error", "Dados inválidos.", details=data)

    if isinstance(exc, drf_exceptions.APIException):
        code = exc.get_codes()
        message = exc.detail
        return build_error_body(
            code if isinstance(code, str) else exc.default_code,
            str(message) if isinstance(message, str) else str(exc.default_detail),
        )

    return build_error_body("request_error", str(data))

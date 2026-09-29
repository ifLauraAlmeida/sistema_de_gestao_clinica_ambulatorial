"""Exceções de domínio convertidas em respostas de API padronizadas."""

from collections.abc import Mapping
from http import HTTPStatus


class DomainError(Exception):
    """
    Violação de regra de negócio.

    `code` é estável e pode ser usado pelo frontend; `message` é exibível ao
    usuário e não deve conter dados sensíveis.

    Exemplo:
        raise DomainError("A senha informada já foi finalizada.", code="queue_entry_finished")
    """

    status_code: int = HTTPStatus.BAD_REQUEST
    default_code: str = "domain_error"

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        details: Mapping[str, list[str]] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code or self.default_code
        # Erros por campo, no mesmo formato de `details` da validação da API.
        self.details = dict(details) if details else None


class AccessDeniedError(DomainError):
    """Usuário autenticado sem autorização contextual para a operação."""

    status_code = HTTPStatus.FORBIDDEN
    default_code = "permission_denied"


class ResourceNotFoundError(DomainError):
    """Recurso inexistente ou fora do alcance do usuário."""

    status_code = HTTPStatus.NOT_FOUND
    default_code = "not_found"


class StateConflictError(DomainError):
    """Operação incompatível com o estado atual do recurso."""

    status_code = HTTPStatus.CONFLICT
    default_code = "conflict"

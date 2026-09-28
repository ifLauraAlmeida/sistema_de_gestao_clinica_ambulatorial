"""Login e logout por sessão do Django, com auditoria."""

from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest

from apps.accounts.models import User
from apps.audit.actions import AuditAction
from apps.audit.services import record_request_audit_event
from apps.core.exceptions import DomainError

# Limite do campo username do Django; evita gravar entradas arbitrariamente longas.
_MAX_AUDITED_USERNAME_LENGTH = 150


class InvalidCredentialsError(DomainError):
    """Usuário/senha incorretos ou conta inativa (indistinguíveis por segurança)."""

    status_code = 401
    default_code = "invalid_credentials"


def login_user(request: HttpRequest, *, username: str, password: str) -> User:
    """
    Autentica e inicia a sessão do usuário.

    Falhas geram LOGIN_FAILED sem registrar a senha. A mensagem de erro não
    revela se o usuário existe.

    Exemplo:
        user = login_user(request, username="ana.recepcao", password="...")
    """
    user = authenticate(request, username=username, password=password)
    if not isinstance(user, User):
        record_request_audit_event(
            request,
            action=AuditAction.LOGIN_FAILED,
            metadata={"username": username[:_MAX_AUDITED_USERNAME_LENGTH]},
        )
        raise InvalidCredentialsError("Usuário ou senha inválidos.")

    login(request, user)
    record_request_audit_event(
        request, action=AuditAction.LOGIN_SUCCESS, entity_type="user", entity_id=str(user.pk)
    )
    return user


def logout_user(request: HttpRequest) -> None:
    """
    Registra o logout e encerra a sessão Django.

    Exemplo:
        logout_user(request)
    """
    record_request_audit_event(request, action=AuditAction.LOGOUT)
    logout(request)

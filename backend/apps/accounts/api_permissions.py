"""Verificação de permissões por perfil nos endpoints da API."""

from collections.abc import Mapping

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.accounts.access_permissions import AccessPermission, user_has_permission
from apps.accounts.models import User
from apps.audit.actions import AuditAction
from apps.audit.services import record_request_audit_event

# Uma permissão, ou uma tupla em que qualquer uma das permissões é suficiente
# (ex.: chamar da própria fila OU de qualquer fila).
RequiredPermission = AccessPermission | tuple[AccessPermission, ...]


def get_required_permissions(view: APIView, http_method: str) -> tuple[AccessPermission, ...]:
    """Permissões aceitas pela view para o método HTTP; vazio quando não declarado."""
    declared: Mapping[str, RequiredPermission] = getattr(view, "required_permissions", {})
    required = declared.get(http_method)
    if required is None:
        return ()
    return required if isinstance(required, tuple) else (required,)


class HasRequiredAccessPermission(BasePermission):
    """
    Exige que o perfil do usuário possua a permissão declarada pela view.

    A view declara `required_permissions = {"GET": AccessPermission.X, ...}`;
    uma tupla indica que qualquer uma das permissões basta. Métodos não
    declarados são negados (negado por padrão). Negações de usuários
    autenticados geram evento de auditoria.
    """

    message = "Seu perfil não tem permissão para esta operação."

    def has_permission(self, request: Request, view: APIView) -> bool:
        user = request.user
        if not isinstance(user, User):
            return False

        required = get_required_permissions(view, request.method or "")
        if any(user_has_permission(user, permission) for permission in required):
            return True

        record_request_audit_event(
            request,
            action=AuditAction.ACCESS_DENIED,
            entity_type="endpoint",
            metadata={
                "method": request.method,
                "path": request.path,
                "required_permission": ",".join(required) or None,
            },
        )
        return False

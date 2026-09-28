"""Verificação de permissões por perfil nos endpoints da API."""

from collections.abc import Mapping

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.accounts.access_permissions import AccessPermission, user_has_permission
from apps.accounts.models import User
from apps.audit.actions import AuditAction
from apps.audit.services import record_request_audit_event


def get_required_permission(view: APIView, http_method: str) -> AccessPermission | None:
    """Retorna a permissão exigida pela view para o método HTTP, se declarada."""
    required: Mapping[str, AccessPermission] = getattr(view, "required_permissions", {})
    return required.get(http_method)


class HasRequiredAccessPermission(BasePermission):
    """
    Exige que o perfil do usuário possua a permissão declarada pela view.

    A view declara `required_permissions = {"GET": AccessPermission.X, ...}`.
    Métodos não declarados são negados (negado por padrão). Negações de
    usuários autenticados geram evento de auditoria.
    """

    message = "Seu perfil não tem permissão para esta operação."

    def has_permission(self, request: Request, view: APIView) -> bool:
        user = request.user
        if not isinstance(user, User):
            return False

        required = get_required_permission(view, request.method or "")
        if required is not None and user_has_permission(user, required):
            return True

        record_request_audit_event(
            request,
            action=AuditAction.ACCESS_DENIED,
            entity_type="endpoint",
            metadata={
                "method": request.method,
                "path": request.path,
                "required_permission": str(required) if required else None,
            },
        )
        return False

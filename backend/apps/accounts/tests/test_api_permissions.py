import pytest
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.views import APIView

from apps.accounts.access_permissions import AccessPermission
from apps.accounts.api_permissions import HasRequiredAccessPermission
from apps.accounts.models import UserRole
from apps.accounts.tests.factories import create_user
from apps.audit.models import AuditEvent


class AuditProtectedView(APIView):
    permission_classes = (HasRequiredAccessPermission,)
    required_permissions = {"GET": AccessPermission.AUDIT_VIEW}

    def get(self, request):
        return Response({"ok": True})

    def post(self, request):
        return Response({"ok": True})


def _request(method: str, user=None):
    request = getattr(APIRequestFactory(), method)("/api/v1/teste/")
    if user is not None:
        force_authenticate(request, user=user)
    return AuditProtectedView.as_view()(request)


@pytest.mark.django_db
def test_allows_role_with_declared_permission():
    response = _request("get", create_user("gestor.perm", UserRole.GESTOR))

    assert response.status_code == 200


@pytest.mark.django_db
def test_denies_role_without_permission_and_audits_attempt():
    atendente = create_user("atendente.perm", UserRole.ATENDENTE)

    response = _request("get", atendente)

    assert response.status_code == 403
    event = AuditEvent.objects.get(action="ACCESS_DENIED")
    assert event.user == atendente
    assert event.metadata["required_permission"] == "audit.view"


@pytest.mark.django_db
def test_undeclared_method_is_denied_by_default():
    response = _request("post", create_user("gestor.post", UserRole.GESTOR))

    assert response.status_code == 403


@pytest.mark.django_db
def test_anonymous_request_is_rejected_without_audit():
    response = _request("get")

    assert response.status_code in (401, 403)
    assert not AuditEvent.objects.exists()


class AnyOfProtectedView(APIView):
    permission_classes = (HasRequiredAccessPermission,)
    required_permissions = {
        "GET": (AccessPermission.CLINICAL_QUEUE_CALL_OWN, AccessPermission.CLINICAL_QUEUE_CALL_ANY)
    }

    def get(self, request):
        return Response({"ok": True})


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("role", "expected_status"),
    [(UserRole.MEDICO, 200), (UserRole.GESTOR, 200), (UserRole.ATENDENTE, 403)],
)
def test_tuple_of_permissions_accepts_any_of_them(role, expected_status):
    request = APIRequestFactory().get("/api/v1/teste/")
    force_authenticate(request, user=create_user(f"user.{role}", role))

    response = AnyOfProtectedView.as_view()(request)

    assert response.status_code == expected_status

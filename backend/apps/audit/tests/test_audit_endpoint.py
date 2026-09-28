import pytest

from apps.audit.actions import AuditAction
from apps.audit.services import record_audit_event

pytestmark = pytest.mark.django_db

URL = "/api/v1/audit/events/"


def test_gestor_lists_and_filters_audit_events(client_for, gestor, medico):
    record_audit_event(action=AuditAction.LOGIN_SUCCESS, user=medico)
    record_audit_event(action=AuditAction.MEDICAL_RECORD_VIEW_DENIED, user=medico)

    response = client_for(gestor).get(URL, {"action": "MEDICAL_RECORD_VIEW_DENIED"})

    assert response.status_code == 200
    [event] = response.json()["results"]
    assert event["username"] == "bruno.medico"


@pytest.mark.parametrize("user_fixture", ["atendente", "medico"])
def test_other_roles_cannot_read_audit(client_for, request, user_fixture):
    user = request.getfixturevalue(user_fixture)

    assert client_for(user).get(URL).status_code == 403

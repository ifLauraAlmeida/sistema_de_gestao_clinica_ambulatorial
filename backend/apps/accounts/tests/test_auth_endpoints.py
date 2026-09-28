import pytest
from rest_framework.test import APIClient

from apps.accounts.models import UserRole
from apps.accounts.tests.factories import create_user
from apps.audit.models import AuditEvent

PASSWORD = "senha-de-teste-123"


def _csrf_client() -> tuple[APIClient, str]:
    client = APIClient(enforce_csrf_checks=True)
    response = client.get("/api/v1/auth/csrf/")
    assert response.status_code == 204
    return client, response.cookies["csrftoken"].value


def _login(client: APIClient, token: str, username: str, password: str = PASSWORD):
    return client.post(
        "/api/v1/auth/login/",
        {"username": username, "password": password},
        format="json",
        HTTP_X_CSRFTOKEN=token,
    )


@pytest.mark.django_db
def test_login_with_valid_credentials_creates_session_and_returns_profile(atendente):
    client, token = _csrf_client()

    response = _login(client, token, "ana.recepcao")

    assert response.status_code == 200
    body = response.json()
    assert body["role"] == "ATENDENTE"
    assert "patient.create" in body["permissions"]
    assert "sessionid" in response.cookies
    assert AuditEvent.objects.filter(action="LOGIN_SUCCESS", user=atendente).exists()


@pytest.mark.django_db
def test_login_with_invalid_password_is_rejected_and_audited(atendente):
    client, token = _csrf_client()

    response = _login(client, token, "ana.recepcao", "senha-errada")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_credentials"
    event = AuditEvent.objects.get(action="LOGIN_FAILED")
    assert event.metadata == {"username": "ana.recepcao"}
    assert "senha-errada" not in str(event.metadata)


@pytest.mark.django_db
def test_login_of_inactive_user_is_rejected(db):
    user = create_user("inativo", UserRole.ATENDENTE)
    user.is_active = False
    user.save()
    client, token = _csrf_client()

    assert _login(client, token, "inativo").status_code == 401


@pytest.mark.django_db
def test_login_without_csrf_token_is_rejected(atendente):
    client = APIClient(enforce_csrf_checks=True)

    response = client.post(
        "/api/v1/auth/login/", {"username": "ana.recepcao", "password": PASSWORD}, format="json"
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_login_requires_username_and_password(db):
    client, token = _csrf_client()

    response = client.post("/api/v1/auth/login/", {}, format="json", HTTP_X_CSRFTOKEN=token)

    assert response.status_code == 400
    assert set(response.json()["error"]["details"]) == {"username", "password"}


@pytest.mark.django_db
def test_me_requires_authentication(api_client):
    response = api_client.get("/api/v1/auth/me/")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "not_authenticated"


@pytest.mark.django_db
def test_me_returns_authenticated_user(client_for, medico):
    response = client_for(medico).get("/api/v1/auth/me/")

    assert response.status_code == 200
    assert response.json()["username"] == "bruno.medico"
    assert response.json()["role_label"] == "Médico"


@pytest.mark.django_db
def test_logout_ends_session_and_is_audited(gestor):
    client, token = _csrf_client()
    _login(client, token, "diego.gestor")
    token = client.cookies["csrftoken"].value

    response = client.post("/api/v1/auth/logout/", HTTP_X_CSRFTOKEN=token)

    assert response.status_code == 204
    assert client.get("/api/v1/auth/me/").status_code == 401
    assert AuditEvent.objects.filter(action="LOGOUT", user=gestor).exists()


@pytest.mark.django_db
def test_logout_without_csrf_token_is_rejected(gestor):
    client, token = _csrf_client()
    _login(client, token, "diego.gestor")

    assert client.post("/api/v1/auth/logout/").status_code == 403

from decimal import Decimal

import pytest
from django.db import IntegrityError

from apps.audit.models import AuditEvent
from apps.billing.models import BillingStatus, EncounterBilling, HealthInsurer, PayerType
from apps.catalog.tests.factories import create_service
from apps.professionals.selectors import get_active_professional_for_user
from apps.queues.tests.factories import check_in_new_patient, ensure_professional

pytestmark = pytest.mark.django_db

DAY_URL = "/api/v1/billing/day/"


@pytest.fixture
def insurer(db):
    return HealthInsurer.objects.create(name="Convênio Alfa Saúde")


@pytest.fixture
def encounter(medico, atendente):
    ensure_professional(medico)
    specialty = get_active_professional_for_user(medico).specialties.get()
    service = create_service(
        "Consulta de teste",
        specialty=specialty,
        category="Consultas e atendimentos",
        group="Teste",
        reference_price=Decimal("280.00"),
    )
    return check_in_new_patient(medico, atendente, "Paciente Pagante", service)


def _payment_url(encounter):
    return f"/api/v1/billing/encounters/{encounter.id}/payment/"


def _authorization_url(encounter):
    return f"/api/v1/billing/encounters/{encounter.id}/authorization/"


def test_day_lists_patients_as_pending_with_reference_price(client_for, gestor, encounter):
    response = client_for(gestor).get(DAY_URL)

    assert response.status_code == 200
    [entry] = response.json()["entries"]
    assert entry["patient_name"] == "Paciente Pagante"
    assert entry["status"] == "PENDENTE"
    assert entry["amount"] == "280.00"
    assert response.json()["today"]["pending"] == 1


def test_gestor_confirms_private_payment(client_for, gestor, encounter):
    client = client_for(gestor)

    response = client.post(
        _payment_url(encounter),
        {"payment_method": "PIX", "amount": "150.00"},
        format="json",
    )

    assert response.status_code == 200
    assert response.json()["status"] == "PAGO"
    assert response.json()["payer_label"] == "Particular"
    summary = client.get(DAY_URL).json()["today"]
    assert summary == {"paid": 1, "pending": 0, "released": 0, "received_amount": "150.00"}
    event = AuditEvent.objects.get(action="BILLING_PAYMENT_CONFIRMED")
    assert event.metadata["previous_status"] == "PENDENTE"
    assert event.metadata["new_status"] == "PAGO"


def test_gestor_releases_insurance_authorization(client_for, gestor, encounter, insurer):
    response = client_for(gestor).post(
        _authorization_url(encounter),
        {"insurer": str(insurer.id), "guide_number": "9988776", "amount": "420.00"},
        format="json",
    )

    assert response.status_code == 200
    body = response.json()
    assert (body["status"], body["payer_label"], body["guide_number"]) == (
        "LIBERADO",
        "Convênio Alfa Saúde",
        "9988776",
    )
    assert AuditEvent.objects.filter(action="BILLING_AUTHORIZATION_RELEASED").exists()


def test_authorization_requires_guide_number(client_for, gestor, encounter, insurer):
    response = client_for(gestor).post(
        _authorization_url(encounter), {"insurer": str(insurer.id), "amount": "10"}, format="json"
    )

    assert response.status_code == 400
    assert "guide_number" in response.json()["error"]["details"]


def test_database_rejects_release_without_guide(encounter, gestor, insurer):
    with pytest.raises(IntegrityError):
        EncounterBilling.objects.create(
            encounter=encounter,
            payer_type=PayerType.CONVENIO,
            insurer=insurer,
            amount=Decimal("1"),
            status=BillingStatus.LIBERADO,
            updated_by=gestor,
        )


def test_summary_compares_with_previous_day(client_for, gestor, encounter):
    body = client_for(gestor).get(DAY_URL).json()

    assert body["previous_day"] == {
        "paid": 0,
        "pending": 0,
        "released": 0,
        "received_amount": "0",
    }


@pytest.mark.parametrize("user_fixture", ["atendente", "medico"])
def test_only_gestor_accesses_financial_data(client_for, request, user_fixture, encounter):
    client = client_for(request.getfixturevalue(user_fixture))

    assert client.get(DAY_URL).status_code == 403
    assert client.get("/api/v1/billing/insurers/").status_code == 403
    assert (
        client.post(
            _payment_url(encounter), {"payment_method": "PIX", "amount": "1"}, format="json"
        ).status_code
        == 403
    )
    assert not EncounterBilling.objects.exists()

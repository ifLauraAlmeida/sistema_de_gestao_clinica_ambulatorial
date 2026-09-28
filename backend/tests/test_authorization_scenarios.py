"""
Cenários de autorização exigidos para a fundação do sistema (1 a 30).

Cada teste referencia o número do cenário. Todas as verificações são feitas
diretamente contra a API: o backend precisa negar acessos independentemente do
que o frontend exibe ou oculta.
"""

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.access_permissions import AccessPermission, user_has_permission
from apps.audit.models import AuditEvent
from apps.encounters.models import Encounter
from apps.patients.tests.factories import build_fake_cpf, create_patient
from apps.professionals.selectors import get_active_professional_for_user
from apps.queues.models import QueueCall
from apps.queues.tests.factories import (
    check_in_new_patient,
    ensure_professional,
    place_in_clinical_queue,
    reception_entry_of,
)
from apps.scheduling.tests.factories import create_appointment
from apps.workstations.services import start_work_session
from apps.workstations.tests.factories import create_consultation_room, create_reception_desk

pytestmark = pytest.mark.django_db

API = "/api/v1"


def record_url(encounter_id) -> str:
    return f"{API}/encounters/{encounter_id}/medical-record/"


def history_url(encounter_id) -> str:
    return f"{API}/encounters/{encounter_id}/clinical-history/"


def clinical_call_url(entry) -> str:
    return f"{API}/clinical-queue/{entry.id}/call/"


def reception_call_url(entry) -> str:
    return f"{API}/reception-queue/{entry.id}/call/"


def complete_url(entry) -> str:
    return f"{API}/encounters/{entry.encounter_id}/complete/"


@pytest.fixture
def guiche():
    return create_reception_desk("Guichê 04")


@pytest.fixture
def consultorio():
    return create_consultation_room("Consultório 03")


@pytest.fixture
def clinical_entry(medico, atendente):
    return place_in_clinical_queue(medico, atendente, "Paciente Fila Ativa")


@pytest.fixture
def other_doctor_entry(outro_medico, atendente, clinical_entry):
    return place_in_clinical_queue(outro_medico, atendente, "Paciente Outra Médica")


@pytest.fixture
def attended_entry(client_for, medico, clinical_entry, consultorio):
    """Atendimento chamado e finalizado (ATENDIDO) pelo médico."""
    start_work_session(medico, consultorio.id)
    client = client_for(medico)
    assert client.post(clinical_call_url(clinical_entry)).status_code == 201
    assert client.post(complete_url(clinical_entry)).status_code == 200
    return clinical_entry


# ---------------------------------------------------------------------------
# ATENDENTE
# ---------------------------------------------------------------------------


def test_01_atendente_cria_paciente(client_for, atendente):
    response = client_for(atendente).post(
        f"{API}/patients/",
        {
            "full_name": "Paciente Novo",
            "cpf": build_fake_cpf("300400500"),
            "birth_date": "1990-05-01",
        },
        format="json",
    )

    assert response.status_code == 201


def test_02_atendente_visualiza_agenda(client_for, atendente):
    assert client_for(atendente).get(f"{API}/appointments/").status_code == 200


def test_03_atendente_realiza_operacoes_administrativas(client_for, atendente, medico):
    professional = ensure_professional(medico)
    appointment = create_appointment(
        create_patient(), professional, professional.specialties.get(), created_by=atendente
    )
    client = client_for(atendente)

    confirm = client.patch(
        f"{API}/appointments/{appointment.id}/", {"status": "CONFIRMADO"}, format="json"
    )
    check_in = client.post(
        f"{API}/check-ins/", {"appointment_id": str(appointment.id)}, format="json"
    )
    entry = reception_entry_of(Encounter.objects.get(appointment=appointment))
    forward = client.post(f"{API}/reception-queue/{entry.id}/forward/")

    assert (confirm.status_code, check_in.status_code, forward.status_code) == (200, 201, 204)


def test_04_atendente_visualiza_fila_da_recepcao(client_for, atendente, medico):
    check_in_new_patient(medico, atendente)

    response = client_for(atendente).get(f"{API}/reception-queue/")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_05_atendente_seleciona_guiche(client_for, atendente, guiche):
    response = client_for(atendente).post(
        f"{API}/work-sessions/", {"station_id": str(guiche.id)}, format="json"
    )

    assert response.status_code == 201


def test_06_atendente_chama_paciente_para_o_proprio_guiche(client_for, atendente, medico, guiche):
    entry = reception_entry_of(check_in_new_patient(medico, atendente))
    start_work_session(atendente, guiche.id)

    response = client_for(atendente).post(reception_call_url(entry))

    assert response.status_code == 201
    assert response.json()["destination_label"] == "Guichê 04"


def test_07_atendente_nao_acessa_prontuario(client_for, atendente, clinical_entry):
    response = client_for(atendente).get(record_url(clinical_entry.encounter_id))

    assert response.status_code == 403


def test_08_atendente_nao_acessa_historico_clinico(client_for, atendente, clinical_entry):
    response = client_for(atendente).get(history_url(clinical_entry.encounter_id))

    assert response.status_code == 403


def test_09_atendente_nao_acessa_historico_financeiro(client_for, atendente):
    # O módulo financeiro ainda não existe; a permissão já é negada ao perfil
    # e não é entregue ao frontend.
    assert not user_has_permission(atendente, AccessPermission.BILLING_VIEW_HISTORY)
    me = client_for(atendente).get(f"{API}/auth/me/").json()
    assert "billing.view_history" not in me["permissions"]


def test_10_atendente_nao_acessa_fila_clinica(client_for, atendente, clinical_entry):
    client = client_for(atendente)

    assert client.get(f"{API}/clinical-queue/").status_code == 403
    assert client.get(f"{API}/clinical-queue/", {"status": "inactive"}).status_code == 403


def test_11_atendente_nao_chama_para_consultorio(
    client_for, atendente, clinical_entry, guiche, consultorio
):
    client = client_for(atendente)
    start_work_session(atendente, guiche.id)

    room_session = client.post(
        f"{API}/work-sessions/", {"station_id": str(consultorio.id)}, format="json"
    )
    call = client.post(clinical_call_url(clinical_entry))

    assert room_session.status_code == 403
    assert call.status_code == 403
    assert not QueueCall.objects.exists()


# ---------------------------------------------------------------------------
# MÉDICO
# ---------------------------------------------------------------------------


def test_12_medico_seleciona_sala(client_for, medico, consultorio):
    response = client_for(medico).post(
        f"{API}/work-sessions/", {"station_id": str(consultorio.id)}, format="json"
    )

    assert response.status_code == 201
    assert response.json()["station"]["name"] == "Consultório 03"


def test_13_medico_visualiza_propria_fila_ativa(client_for, medico, clinical_entry):
    response = client_for(medico).get(f"{API}/clinical-queue/")

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [str(clinical_entry.id)]


def test_14_medico_visualiza_propria_fila_inativa(client_for, medico, attended_entry):
    response = client_for(medico).get(f"{API}/clinical-queue/", {"status": "inactive"})

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [str(attended_entry.id)]


def test_15_medico_nao_visualiza_fila_de_outro_medico(
    client_for, medico, outro_medico, other_doctor_entry
):
    other_professional = get_active_professional_for_user(outro_medico)
    client = client_for(medico)

    own_queue = client.get(f"{API}/clinical-queue/").json()
    forced = client.get(f"{API}/clinical-queue/", {"professional_id": str(other_professional.id)})

    assert str(other_doctor_entry.id) not in [item["id"] for item in own_queue]
    assert forced.status_code == 403


def test_16_medico_acessa_prontuario_da_propria_fila_ativa(client_for, medico, clinical_entry):
    assert client_for(medico).get(record_url(clinical_entry.encounter_id)).status_code == 200


def test_17_medico_acessa_historico_clinico_da_propria_fila_ativa(
    client_for, medico, clinical_entry
):
    assert client_for(medico).get(history_url(clinical_entry.encounter_id)).status_code == 200


def test_18_medico_nao_acessa_prontuario_fora_da_propria_fila_ativa(
    client_for, medico, atendente, other_doctor_entry
):
    still_in_reception = check_in_new_patient(medico, atendente, "Paciente na Recepção")
    client = client_for(medico)

    assert client.get(record_url(other_doctor_entry.encounter_id)).status_code == 403
    assert client.get(record_url(still_in_reception.id)).status_code == 403


def test_19_medico_chama_somente_pacientes_autorizados(
    client_for, medico, clinical_entry, other_doctor_entry, consultorio
):
    start_work_session(medico, consultorio.id)
    client = client_for(medico)

    assert client.post(clinical_call_url(clinical_entry)).status_code == 201
    assert client.post(clinical_call_url(other_doctor_entry)).status_code == 403
    assert client.post(reception_call_url(clinical_entry)).status_code == 403


def test_20_medico_precisa_de_sala_ativa_para_chamar(client_for, medico, clinical_entry):
    response = client_for(medico).post(clinical_call_url(clinical_entry))

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "work_session_required"


def test_21_medico_marca_atendimento_como_atendido(client_for, medico, attended_entry):
    encounter = Encounter.objects.get(pk=attended_entry.encounter_id)

    assert encounter.status == "ATENDIDO"


def test_22_atendido_sai_da_fila_ativa(client_for, medico, attended_entry):
    assert client_for(medico).get(f"{API}/clinical-queue/").json() == []


def test_23_atendimento_permanece_na_fila_inativa(client_for, medico, attended_entry):
    [item] = client_for(medico).get(f"{API}/clinical-queue/", {"status": "inactive"}).json()

    assert item["encounter_status"] == "ATENDIDO"
    assert item["patient_name"] == "Paciente Fila Ativa"


def test_24_vinculo_historico_permanece_armazenado(medico, attended_entry):
    encounter = Encounter.objects.get(pk=attended_entry.encounter_id)

    assert encounter.professional.user == medico
    assert encounter.patient.full_name == "Paciente Fila Ativa"
    assert encounter.completed_at is not None
    assert QueueCall.objects.get().destination_label == "Consultório 03"


def test_25_apos_finalizacao_vinculo_nao_permite_acesso_clinico(client_for, medico, attended_entry):
    client = client_for(medico)

    assert client.get(record_url(attended_entry.encounter_id)).status_code == 403
    assert client.get(history_url(attended_entry.encounter_id)).status_code == 403


# ---------------------------------------------------------------------------
# GESTOR
# ---------------------------------------------------------------------------


def test_26_gestor_possui_acesso_administrativo_total(client_for, gestor, clinical_entry):
    client = client_for(gestor)
    reads = [
        f"{API}/patients/",
        f"{API}/appointments/",
        f"{API}/reception-queue/",
        f"{API}/reception-queue/calls/",
        f"{API}/clinical-queue/",
        f"{API}/clinical-queue/?status=inactive",
        f"{API}/audit/events/",
        f"{API}/work-sessions/stations/",
        record_url(clinical_entry.encounter_id),
        history_url(clinical_entry.encounter_id),
    ]

    assert {url: client.get(url).status_code for url in reads} == dict.fromkeys(reads, 200)
    assert client.get(f"{API}/auth/me/").json()["required_station_type"] is None


# ---------------------------------------------------------------------------
# SEGURANÇA
# ---------------------------------------------------------------------------


PROTECTED_READS = [
    "/patients/",
    "/appointments/",
    "/reception-queue/",
    "/clinical-queue/",
    "/audit/events/",
    "/work-sessions/stations/",
    "/auth/me/",
]


@pytest.mark.parametrize("path", PROTECTED_READS)
def test_27_requisicao_direta_sem_sessao_e_negada(path):
    assert APIClient().get(f"{API}{path}").status_code == 401


def test_27_requisicao_direta_autenticada_nao_contorna_perfil(
    client_for, atendente, medico, clinical_entry
):
    attendant = client_for(atendente)
    doctor = client_for(medico)

    assert attendant.post(complete_url(clinical_entry)).status_code == 403
    assert attendant.get(f"{API}/audit/events/").status_code == 403
    assert doctor.post(f"{API}/patients/", {}, format="json").status_code == 403
    assert doctor.get(f"{API}/reception-queue/").status_code == 403


def test_28_manipulacao_do_frontend_nao_contorna_permissoes(
    client_for, atendente, medico, outro_medico, clinical_entry, other_doctor_entry, consultorio
):
    attendant = client_for(atendente)
    doctor = client_for(medico)
    other_professional = get_active_professional_for_user(outro_medico)

    # Parâmetros forjados (perfil, profissional) não alteram a decisão do backend.
    assert attendant.get(f"{API}/audit/events/?role=GESTOR").status_code == 403
    assert attendant.get(f"{API}/clinical-queue/", HTTP_X_USER_ROLE="GESTOR").status_code == 403
    assert (
        doctor.get(
            f"{API}/clinical-queue/", {"professional_id": str(other_professional.id)}
        ).status_code
        == 403
    )
    # Médico em consultório não chama paciente de outra médica nem finaliza atendimento alheio.
    start_work_session(medico, consultorio.id)
    assert doctor.post(clinical_call_url(other_doctor_entry)).status_code == 403
    assert doctor.post(complete_url(other_doctor_entry)).status_code == 403
    # Atendente não ocupa consultório enviando o id de uma sala.
    assert (
        attendant.post(
            f"{API}/work-sessions/", {"station_id": str(consultorio.id)}, format="json"
        ).status_code
        == 403
    )


def test_29_acesso_clinico_indevido_retorna_resposta_apropriada(
    client_for, medico, other_doctor_entry
):
    response = client_for(medico).get(record_url(other_doctor_entry.encounter_id))

    assert response.status_code == 403
    assert response.json() == {
        "error": {
            "code": "medical_record_access_denied",
            "message": "Acesso ao prontuário não autorizado para este atendimento.",
        }
    }
    assert "Paciente Outra Médica" not in response.content.decode()


def test_30_acesso_clinico_indevido_gera_auditoria(
    client_for, atendente, medico, other_doctor_entry
):
    client_for(medico).get(record_url(other_doctor_entry.encounter_id))
    client_for(atendente).get(history_url(other_doctor_entry.encounter_id))

    denied = AuditEvent.objects.filter(action="MEDICAL_RECORD_VIEW_DENIED").order_by("timestamp")
    assert [(event.user, event.entity_id) for event in denied] == [
        (medico, str(other_doctor_entry.encounter_id)),
        (atendente, str(other_doctor_entry.encounter_id)),
    ]
    assert all(event.timestamp <= timezone.now() for event in denied)

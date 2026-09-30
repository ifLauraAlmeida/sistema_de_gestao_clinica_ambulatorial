import pytest
from django.core.management import CommandError, call_command
from django.test import override_settings

from apps.accounts.models import User
from apps.billing.models import EncounterBilling
from apps.catalog.models import Service
from apps.patients.models import Patient
from apps.queues.models import QueueEntry
from apps.scheduling.models import Appointment

pytestmark = pytest.mark.django_db

PASSWORD = "senha-demo-local"


@override_settings(DEBUG=True)
def test_seed_creates_fictitious_flow_and_is_idempotent():
    call_command("seed_demo_data", password=PASSWORD)
    call_command("seed_demo_data", password=PASSWORD)

    assert set(User.objects.values_list("role", flat=True)) == {
        "ATENDENTE",
        "MEDICO",
        "PROFISSIONAL_SAUDE",
        "TECNICO",
        "GESTOR",
    }
    assert QueueEntry.objects.filter(queue_type="CLINICAL").count() == 4
    assert QueueEntry.objects.filter(queue_type="RECEPTION", status="WAITING").count() == 2
    x_ray = Appointment.objects.get(service__name="Raio-X de joelho")
    assert x_ray.professional.user.username == "tecnico.rx"
    assert x_ray.laterality == "DIREITA"
    collection = Appointment.objects.get(service__name="Coleta de exames laboratoriais")
    assert collection.laboratory_exams.count() == 3
    assert Service.objects.count() > 150
    assert EncounterBilling.objects.filter(status="PAGO").count() == 2
    assert EncounterBilling.objects.filter(status="LIBERADO").count() == 2
    assert Service.objects.get(name="Raio-X de joelho").reference_price == 150
    assert User.objects.get(username="recepcao.demo").check_password(PASSWORD)
    assert not Patient.objects.filter(phone="").exists()


@override_settings(DEBUG=False)
def test_seed_is_refused_without_debug():
    with pytest.raises(CommandError):
        call_command("seed_demo_data", password=PASSWORD)


@override_settings(DEBUG=True)
def test_seed_requires_a_password():
    with pytest.raises(CommandError):
        call_command("seed_demo_data", password="curta")

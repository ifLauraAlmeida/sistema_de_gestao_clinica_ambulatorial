import pytest
from django.core.management import CommandError, call_command
from django.test import override_settings

from apps.accounts.models import User
from apps.patients.models import Patient
from apps.queues.models import QueueEntry

pytestmark = pytest.mark.django_db

PASSWORD = "senha-demo-local"


@override_settings(DEBUG=True)
def test_seed_creates_fictitious_flow_and_is_idempotent():
    call_command("seed_demo_data", password=PASSWORD)
    call_command("seed_demo_data", password=PASSWORD)

    assert set(User.objects.values_list("role", flat=True)) == {"ATENDENTE", "MEDICO", "GESTOR"}
    assert QueueEntry.objects.filter(queue_type="CLINICAL").count() == 3
    assert QueueEntry.objects.filter(queue_type="RECEPTION", status="WAITING").count() == 3
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

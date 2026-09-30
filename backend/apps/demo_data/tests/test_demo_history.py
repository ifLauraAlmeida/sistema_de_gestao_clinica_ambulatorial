from datetime import timedelta

import pytest
from django.core.management import CommandError, call_command
from django.test import override_settings
from django.utils import timezone

from apps.audit.models import AuditEvent
from apps.billing.models import EncounterBilling
from apps.encounters.models import Encounter
from apps.medical_records.models import ClinicalNote
from apps.procedures.models import ProcedureRecord
from apps.queues.models import QueueCall
from apps.scheduling.models import Appointment

pytestmark = pytest.mark.django_db


@pytest.fixture
def demo_base():
    with override_settings(DEBUG=True):
        call_command("seed_demo_data", password="senha-demo-local")


@override_settings(DEBUG=True)
def test_history_covers_the_whole_flow_with_past_timestamps(demo_base):
    call_command("seed_demo_history", months=1, future_days=5)
    today = timezone.localdate()

    past = Encounter.objects.filter(service_date__lt=today - timedelta(days=1))
    assert past.count() > 50
    assert past.filter(status="ATENDIDO").exists()
    assert (
        past.filter(status="NAO_COMPARECEU").exists()
        or Appointment.objects.filter(status="NAO_COMPARECEU").exists()
    )
    assert ClinicalNote.objects.filter(created_at__date__lt=today).exists()
    assert ProcedureRecord.objects.filter(recorded_at__date__lt=today).exists()
    assert QueueCall.objects.filter(called_at__date__lt=today).exists()
    assert EncounterBilling.objects.filter(status="PAGO").exists()
    assert EncounterBilling.objects.filter(status="LIBERADO").exists()
    assert AuditEvent.objects.filter(timestamp__date__lt=today, action="LOGIN_SUCCESS").exists()
    assert Appointment.objects.filter(scheduled_for__date__gt=today, status="CONFIRMADO").exists()
    completed = past.filter(status="ATENDIDO").first()
    assert completed.completed_at > completed.checked_in_at


@override_settings(DEBUG=True)
def test_history_is_not_generated_twice(demo_base):
    call_command("seed_demo_history", months=1, future_days=0)
    total = Encounter.objects.count()

    call_command("seed_demo_history", months=1, future_days=0)

    assert Encounter.objects.count() == total


@override_settings(DEBUG=False)
def test_history_requires_debug():
    with pytest.raises(CommandError):
        call_command("seed_demo_history")

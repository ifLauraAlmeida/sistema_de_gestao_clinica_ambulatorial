"""Acúmulo de registros de um dia de histórico para gravação em lote."""

from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime

from apps.accounts.models import User
from apps.audit.actions import AuditAction
from apps.audit.models import AuditEvent
from apps.billing.models import EncounterBilling
from apps.catalog.models import LaboratoryExam
from apps.encounters.models import Encounter, EncounterStatusChange
from apps.medical_records.models import ClinicalNote
from apps.procedures.models import ProcedureRecord
from apps.queues.models import QueueCall, QueueEntry
from apps.scheduling.models import Appointment
from apps.workstations.models import WorkSession

AuditMetadata = Mapping[str, str | int | bool | None]


@dataclass
class DayBatch:
    """
    Registros de um dia, gravados em ordem de dependência com bulk_create.

    Chaves UUID são geradas no Python, então as referências entre objetos já
    existem antes da gravação.
    """

    work_sessions: list[WorkSession] = field(default_factory=list)
    appointments: list[Appointment] = field(default_factory=list)
    laboratory_links: list[tuple[Appointment, list[LaboratoryExam]]] = field(default_factory=list)
    encounters: list[Encounter] = field(default_factory=list)
    status_changes: list[EncounterStatusChange] = field(default_factory=list)
    queue_entries: list[QueueEntry] = field(default_factory=list)
    calls: list[QueueCall] = field(default_factory=list)
    notes: list[ClinicalNote] = field(default_factory=list)
    procedures: list[ProcedureRecord] = field(default_factory=list)
    billings: list[EncounterBilling] = field(default_factory=list)
    audits: list[AuditEvent] = field(default_factory=list)
    ticket_counters: dict[str, int] = field(default_factory=lambda: defaultdict(int))

    def next_ticket(self, prefix: str) -> str:
        self.ticket_counters[prefix] += 1
        return f"{prefix}{self.ticket_counters[prefix]:02d}"

    def audit(
        self,
        action: AuditAction,
        user: User | None,
        at: datetime,
        *,
        entity_type: str = "",
        entity_id: str = "",
        metadata: AuditMetadata | None = None,
    ) -> None:
        # Endereços de rede local fictícios, estáveis por usuário.
        ip = f"10.0.0.{sum(map(ord, user.username)) % 200 + 20}" if user else "10.0.0.250"
        self.audits.append(
            AuditEvent(
                action=action,
                user=user,
                timestamp=at,
                entity_type=entity_type,
                entity_id=entity_id,
                ip_address=ip,
                metadata=dict(metadata or {}),
            )
        )

    def flush(self) -> None:
        """Grava tudo em ordem de dependência (chamar dentro de transação)."""
        WorkSession.objects.bulk_create(self.work_sessions)
        Appointment.objects.bulk_create(self.appointments)
        through = Appointment.laboratory_exams.through
        through.objects.bulk_create(
            [
                through(appointment_id=appointment.pk, laboratoryexam_id=exam.pk)
                for appointment, exams in self.laboratory_links
                for exam in exams
            ]
        )
        Encounter.objects.bulk_create(self.encounters)
        EncounterStatusChange.objects.bulk_create(self.status_changes)
        QueueEntry.objects.bulk_create(self.queue_entries)
        QueueCall.objects.bulk_create(self.calls)
        ClinicalNote.objects.bulk_create(self.notes)
        ProcedureRecord.objects.bulk_create(self.procedures)
        EncounterBilling.objects.bulk_create(self.billings)
        AuditEvent.objects.bulk_create(self.audits)

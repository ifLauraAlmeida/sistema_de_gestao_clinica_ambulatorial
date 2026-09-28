import type { ReactElement, ReactNode } from 'react';
import { Inbox } from 'lucide-react';
import { Badge, type BadgeTone } from '../ui/Badge';
import { EmptyState } from '../ui/EmptyState';
import { Table, type TableColumn } from '../ui/Table';
import type { QueueEntry, QueueEntryStatus } from '../../types/queue';
import { waitTone, waitingMinutes } from '../../utils/queueMetrics';
import styles from './Queue.module.css';

const STATUS_TONES: Record<QueueEntryStatus, BadgeTone> = {
  WAITING: 'info',
  CALLED: 'warning',
  FINISHED: 'success',
  CANCELLED: 'neutral',
};

interface QueueTableProps {
  caption: string;
  entries: QueueEntry[];
  now: Date;
  showProfessional?: boolean;
  showWaitingTime?: boolean;
  emptyTitle: string;
  renderActions?: (entry: QueueEntry) => ReactNode;
}

export function QueueTable({
  caption,
  entries,
  now,
  showProfessional = false,
  showWaitingTime = true,
  emptyTitle,
  renderActions,
}: QueueTableProps): ReactElement {
  const columns: TableColumn<QueueEntry>[] = [
    { key: 'position', header: '#', render: (_, index) => index + 1 },
    {
      key: 'ticket',
      header: 'Senha',
      render: (entry) => <span className={styles.ticket}>{entry.ticket_code}</span>,
    },
    { key: 'patient', header: 'Paciente', render: (entry) => entry.patient_name },
    { key: 'specialty', header: 'Especialidade', render: (entry) => entry.specialty_name },
    ...(showProfessional
      ? [
          {
            key: 'professional',
            header: 'Profissional',
            render: (e: QueueEntry) => e.professional_name,
          },
        ]
      : []),
    {
      key: 'status',
      header: 'Status',
      render: (entry) => <Badge tone={STATUS_TONES[entry.status]}>{statusLabelOf(entry)}</Badge>,
    },
    ...(showWaitingTime ? [waitingColumn(now)] : []),
    {
      key: 'destination',
      header: 'Último destino',
      render: (entry) => entry.last_call_destination ?? '—',
    },
    ...(renderActions ? [{ key: 'actions', header: 'Ações', render: renderActions }] : []),
  ];

  return (
    <Table
      caption={caption}
      columns={columns}
      rows={entries}
      getRowKey={(entry) => entry.id}
      emptyState={<EmptyState icon={<Inbox size={22} />} title={emptyTitle} />}
    />
  );
}

/** Situação na fila; senhas finalizadas mostram o desfecho do atendimento (ex.: Atendido). */
function statusLabelOf(entry: QueueEntry): string {
  return entry.status === 'FINISHED' ? entry.encounter_status_label : entry.status_label;
}

function waitingColumn(now: Date): TableColumn<QueueEntry> {
  return {
    key: 'waiting',
    header: 'Espera',
    render: (entry) => {
      const minutes = waitingMinutes(entry, now);
      return <Badge tone={waitTone(minutes)}>{minutes} min</Badge>;
    },
  };
}

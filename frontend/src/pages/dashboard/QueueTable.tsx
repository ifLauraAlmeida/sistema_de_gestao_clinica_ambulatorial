import type { ReactElement, ReactNode } from 'react';
import { Inbox } from 'lucide-react';
import { Badge, type BadgeTone } from '../../components/ui/Badge';
import { EmptyState } from '../../components/ui/EmptyState';
import { Table, type TableColumn } from '../../components/ui/Table';
import type { QueueEntry, QueueEntryStatus } from '../../types/queue';
import { waitTone, waitingMinutes } from '../../utils/queueMetrics';
import styles from './Dashboard.module.css';

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
      render: (entry) => (
        <Badge tone={STATUS_TONES[entry.status]}>{entry.encounter_status_label}</Badge>
      ),
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

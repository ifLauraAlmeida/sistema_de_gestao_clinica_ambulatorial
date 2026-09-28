import { useCallback, type ReactElement } from 'react';
import { Link } from 'react-router-dom';
import { CalendarDays, ClipboardCheck, ListOrdered, UserPlus } from 'lucide-react';
import { QueueKpis } from '../../components/queue/QueueKpis';
import { QueueTable } from '../../components/queue/QueueTable';
import { TodayBadge } from '../../components/queue/TodayBadge';
import { QUEUE_REFRESH_INTERVAL_MS } from '../../components/queue/queueRefresh';
import { Badge } from '../../components/ui/Badge';
import { Card } from '../../components/ui/Card';
import { EmptyState } from '../../components/ui/EmptyState';
import { PageHeader } from '../../components/ui/PageHeader';
import { Table } from '../../components/ui/Table';
import { useApiResource } from '../../hooks/useApiResource';
import { useCurrentUser } from '../../hooks/useAuth';
import { useNow } from '../../hooks/useNow';
import { listAgenda } from '../../services/agenda';
import { listReceptionQueue } from '../../services/queues';
import { formatTime, toIsoDate } from '../../utils/dateTime';
import { summarizeQueue } from '../../utils/queueMetrics';
import { firstNameOf } from '../../utils/userAccess';
import grid from '../../layouts/PageGrid.module.css';
import { APPOINTMENT_STATUS_TONES } from '../agenda/agendaRules';
import { canCheckIn } from '../checkIn/checkInRules';
import styles from './ReceptionDashboard.module.css';

const PREVIEW_SIZE = 6;

const SHORTCUTS = [
  { to: '/pacientes', label: 'Novo paciente', icon: <UserPlus size={22} /> },
  { to: '/check-in', label: 'Check-in', icon: <ClipboardCheck size={22} /> },
  { to: '/fila-recepcao', label: 'Fila da recepção', icon: <ListOrdered size={22} /> },
  { to: '/agenda', label: 'Agenda', icon: <CalendarDays size={22} /> },
];

/** Resumo da recepção (Tela 02): indicadores, fila atual e próximas consultas. */
export function ReceptionDashboard(): ReactElement {
  const user = useCurrentUser();
  const now = useNow();
  const queue = useApiResource(listReceptionQueue, {
    refreshIntervalMs: QUEUE_REFRESH_INTERVAL_MS,
  });
  const agendaLoader = useCallback(() => listAgenda({ date: toIsoDate(new Date()) }), []);
  const agenda = useApiResource(agendaLoader, { refreshIntervalMs: QUEUE_REFRESH_INTERVAL_MS });
  const entries = queue.data ?? [];
  const upcoming = (agenda.data ?? []).filter(canCheckIn).slice(0, PREVIEW_SIZE);

  return (
    <>
      <PageHeader
        title={`Olá, ${firstNameOf(user)}!`}
        subtitle="Aqui está o resumo do atendimento de hoje."
        actions={<TodayBadge now={now} />}
      />
      <nav className={styles.shortcuts} aria-label="Atalhos da recepção">
        {SHORTCUTS.map((shortcut) => (
          <Link key={shortcut.to} to={shortcut.to} className={styles.shortcut}>
            {shortcut.icon}
            {shortcut.label}
          </Link>
        ))}
      </nav>
      <QueueKpis summary={summarizeQueue(entries, now)} waitingLabel="Na fila da recepção" />
      <div className={grid.pair}>
        <Card
          title="Fila de atendimento (agora)"
          icon={<ListOrdered size={20} />}
          actions={<Link to="/fila-recepcao">Ver fila completa</Link>}
        >
          <QueueTable
            caption="Fila de atendimento agora"
            entries={entries.slice(0, PREVIEW_SIZE)}
            now={now}
            emptyTitle="Nenhum paciente aguardando na recepção"
          />
        </Card>
        <Card
          title="Próximas consultas"
          icon={<CalendarDays size={20} />}
          actions={<Link to="/agenda">Ver agenda completa</Link>}
        >
          <Table
            caption="Próximas consultas"
            rows={upcoming}
            getRowKey={(appointment) => appointment.id}
            emptyState={<EmptyState title="Nenhuma consulta aguardando chegada" />}
            columns={[
              { key: 'time', header: 'Horário', render: (a) => formatTime(a.scheduled_for) },
              { key: 'patient', header: 'Paciente', render: (a) => a.patient_name },
              { key: 'professional', header: 'Profissional', render: (a) => a.professional_name },
              {
                key: 'status',
                header: 'Situação',
                render: (a) => (
                  <Badge tone={APPOINTMENT_STATUS_TONES[a.status]}>{a.status_label}</Badge>
                ),
              },
            ]}
          />
        </Card>
      </div>
    </>
  );
}

import { useCallback, useState, type FormEvent, type ReactElement } from 'react';
import { CheckCircle2, ClipboardCheck, Search } from 'lucide-react';
import { QUEUE_REFRESH_INTERVAL_MS } from '../../components/queue/queueRefresh';
import { Alert } from '../../components/ui/Alert';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { EmptyState } from '../../components/ui/EmptyState';
import { PhoneLink } from '../../components/ui/PhoneLink';
import { Loading } from '../../components/ui/Loading';
import { PageHeader } from '../../components/ui/PageHeader';
import { Table } from '../../components/ui/Table';
import { TextField } from '../../components/ui/TextField';
import { useApiResource } from '../../hooks/useApiResource';
import { useNow } from '../../hooks/useNow';
import { checkInAppointment, listAgenda } from '../../services/agenda';
import { listReceptionQueue } from '../../services/queues';
import type { Appointment, CheckInResult } from '../../types/agenda';
import { formatTime, toIsoDate } from '../../utils/dateTime';
import { describeError } from '../../utils/errorMessages';
import grid from '../../layouts/PageGrid.module.css';
import { APPOINTMENT_STATUS_TONES, serviceWithLaterality } from '../agenda/agendaRules';
import { canCheckIn } from './checkInRules';
import { ReceptionTodayCard } from './ReceptionTodayCard';
import styles from './CheckInPage.module.css';

/** Registro de chegada do paciente agendado (Tela 05). */
export function CheckInPage(): ReactElement {
  const now = useNow();
  const [searchInput, setSearchInput] = useState('');
  const [search, setSearch] = useState('');
  const [busyId, setBusyId] = useState<string | null>(null);
  const [lastCheckIn, setLastCheckIn] = useState<CheckInResult | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const agendaLoader = useCallback(
    () => listAgenda({ date: toIsoDate(new Date()), search }),
    [search],
  );
  const agenda = useApiResource(agendaLoader);
  const queue = useApiResource(listReceptionQueue, {
    refreshIntervalMs: QUEUE_REFRESH_INTERVAL_MS,
  });

  function handleSearch(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault();
    setSearch(searchInput.trim());
  }

  async function confirmArrival(appointment: Appointment): Promise<void> {
    setBusyId(appointment.id);
    setErrorMessage(null);
    try {
      setLastCheckIn(await checkInAppointment(appointment.id));
      await Promise.all([agenda.reload(), queue.reload()]);
    } catch (error) {
      setErrorMessage(describeError(error, 'Não foi possível registrar a chegada.'));
    } finally {
      setBusyId(null);
    }
  }

  return (
    <>
      <PageHeader
        title="Check-in da recepção"
        subtitle="Localize o paciente, confirme a chegada e encaminhe para a fila."
      />
      {errorMessage && <Alert tone="error">{errorMessage}</Alert>}
      {lastCheckIn && (
        <div className={styles.confirmation} role="status">
          <CheckCircle2 size={28} aria-hidden="true" />
          <div>
            <strong>Chegada registrada: {lastCheckIn.patient_name}</strong>
            <p>
              Senha <span className={styles.ticket}>{lastCheckIn.ticket_code}</span> gerada para{' '}
              {lastCheckIn.service_name ?? lastCheckIn.specialty_name} e incluída na fila da
              recepção.
            </p>
          </div>
        </div>
      )}
      <Card title="Agendamentos de hoje" icon={<ClipboardCheck size={20} />}>
        <form className={styles.searchBar} onSubmit={handleSearch} role="search">
          <TextField
            label="Buscar paciente"
            placeholder="Nome, CPF ou telefone"
            icon={<Search size={18} />}
            value={searchInput}
            onChange={(event) => setSearchInput(event.target.value)}
          />
          <Button type="submit">Buscar</Button>
        </form>
        {agenda.isLoading ? (
          <Loading />
        ) : (
          <Table
            caption="Agendamentos de hoje"
            rows={agenda.data ?? []}
            getRowKey={(appointment) => appointment.id}
            emptyState={<EmptyState title="Nenhum agendamento encontrado para hoje" />}
            columns={[
              { key: 'time', header: 'Horário', render: (a) => formatTime(a.scheduled_for) },
              { key: 'patient', header: 'Paciente', render: (a) => a.patient_name },
              {
                key: 'phone',
                header: 'Telefone',
                render: (a) => <PhoneLink phone={a.patient_phone} />,
              },
              {
                key: 'service',
                header: 'Serviço',
                render: (a) =>
                  a.service_name
                    ? serviceWithLaterality(a.service_name, a.laterality_label)
                    : a.specialty_name,
              },
              { key: 'professional', header: 'Profissional', render: (a) => a.professional_name },
              {
                key: 'status',
                header: 'Status',
                render: (a) => (
                  <Badge tone={APPOINTMENT_STATUS_TONES[a.status]}>{a.status_label}</Badge>
                ),
              },
              { key: 'ticket', header: 'Senha', render: (a) => a.ticket_code ?? '—' },
              {
                key: 'action',
                header: 'Ações',
                render: (a) =>
                  canCheckIn(a) && (
                    <Button
                      icon={<CheckCircle2 size={16} />}
                      isLoading={busyId === a.id}
                      disabled={busyId !== null}
                      onClick={() => void confirmArrival(a)}
                    >
                      Confirmar chegada
                    </Button>
                  ),
              },
            ]}
          />
        )}
      </Card>
      <div className={grid.pair}>
        <ReceptionTodayCard entries={queue.data ?? []} now={now} />
        <Alert tone="info">
          Após a chegada, chame o paciente pela fila da recepção e encaminhe-o para a fila do
          profissional quando estiver liberado.
        </Alert>
      </div>
    </>
  );
}

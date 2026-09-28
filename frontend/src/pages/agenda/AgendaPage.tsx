import { useCallback, useState, type ReactElement } from 'react';
import { CalendarDays, Plus } from 'lucide-react';
import { Alert } from '../../components/ui/Alert';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { EmptyState } from '../../components/ui/EmptyState';
import { Loading } from '../../components/ui/Loading';
import { PageHeader } from '../../components/ui/PageHeader';
import { SelectField } from '../../components/ui/SelectField';
import { Table } from '../../components/ui/Table';
import { TextField } from '../../components/ui/TextField';
import { useApiResource } from '../../hooks/useApiResource';
import { useCurrentUser } from '../../hooks/useAuth';
import { changeAppointmentStatus, listAgenda, listProfessionals } from '../../services/agenda';
import type { AgendaFilters, Appointment, ManualAppointmentStatus } from '../../types/agenda';
import { formatTime, toIsoDate } from '../../utils/dateTime';
import { describeError } from '../../utils/errorMessages';
import { hasAnyPermission } from '../../utils/userAccess';
import grid from '../../layouts/PageGrid.module.css';
import { APPOINTMENT_STATUS_TONES, professionalOptions, specialtyOptions } from './agendaRules';
import { AgendaSummaryCard } from './AgendaSummaryCard';
import { AppointmentDetails } from './AppointmentDetails';
import { NewAppointmentForm } from './NewAppointmentForm';
import styles from './AgendaPage.module.css';

type SidePanel = { kind: 'none' } | { kind: 'details'; id: string } | { kind: 'new' };

/** Agenda de consultas do dia (Tela 04). */
export function AgendaPage(): ReactElement {
  const user = useCurrentUser();
  const [filters, setFilters] = useState<AgendaFilters>({ date: toIsoDate(new Date()) });
  const [panel, setPanel] = useState<SidePanel>({ kind: 'none' });
  const [busyStatus, setBusyStatus] = useState<ManualAppointmentStatus | null>(null);
  const [feedback, setFeedback] = useState<{ tone: 'success' | 'error'; text: string } | null>(
    null,
  );
  const agendaLoader = useCallback(() => listAgenda(filters), [filters]);
  const agenda = useApiResource(agendaLoader);
  const professionals = useApiResource(listProfessionals).data ?? [];
  const appointments = agenda.data ?? [];
  const selected =
    panel.kind === 'details' ? appointments.find((a) => a.id === panel.id) : undefined;

  const updateFilter = (field: 'specialty' | 'professional' | 'date', value: string): void =>
    setFilters((current) =>
      field === 'date' ? { ...current, date: value } : { ...current, [field]: value || undefined },
    );

  async function changeStatus(
    appointment: Appointment,
    status: ManualAppointmentStatus,
  ): Promise<void> {
    setBusyStatus(status);
    setFeedback(null);
    try {
      const updated = await changeAppointmentStatus(appointment.id, status);
      setFeedback({
        tone: 'success',
        text: `Agendamento de ${updated.patient_name}: ${updated.status_label}.`,
      });
      await agenda.reload();
    } catch (error) {
      setFeedback({
        tone: 'error',
        text: describeError(error, 'Não foi possível alterar o agendamento.'),
      });
    } finally {
      setBusyStatus(null);
    }
  }

  function handleCreated(appointment: Appointment): void {
    setFeedback({ tone: 'success', text: `Consulta de ${appointment.patient_name} agendada.` });
    setPanel({ kind: 'details', id: appointment.id });
    void agenda.reload();
  }

  return (
    <>
      <PageHeader
        title="Agenda de consultas"
        subtitle="Visualize, agende e gerencie os atendimentos da clínica."
        actions={
          hasAnyPermission(user, ['appointment.create']) && (
            <Button icon={<Plus size={18} />} onClick={() => setPanel({ kind: 'new' })}>
              Novo agendamento
            </Button>
          )
        }
      />
      <Card>
        <div className={styles.filters}>
          <SelectField
            label="Especialidade"
            placeholder="Todas as especialidades"
            options={specialtyOptions(professionals)}
            value={filters.specialty ?? ''}
            onChange={(event) => updateFilter('specialty', event.target.value)}
          />
          <SelectField
            label="Profissional"
            placeholder="Todos os profissionais"
            options={professionalOptions(professionals)}
            value={filters.professional ?? ''}
            onChange={(event) => updateFilter('professional', event.target.value)}
          />
          <TextField
            label="Data"
            type="date"
            value={filters.date}
            onChange={(event) => event.target.value && updateFilter('date', event.target.value)}
          />
        </div>
      </Card>
      {feedback && <Alert tone={feedback.tone}>{feedback.text}</Alert>}
      <div className={grid.columns}>
        <Card title="Consultas do dia" icon={<CalendarDays size={20} />}>
          {agenda.isLoading ? (
            <Loading />
          ) : (
            <Table
              caption="Consultas do dia"
              rows={appointments}
              getRowKey={(appointment) => appointment.id}
              emptyState={
                <EmptyState icon={<CalendarDays size={22} />} title="Nenhuma consulta nesta data" />
              }
              columns={[
                { key: 'time', header: 'Horário', render: (a) => formatTime(a.scheduled_for) },
                {
                  key: 'patient',
                  header: 'Paciente',
                  render: (a) => (
                    <button
                      type="button"
                      className={styles.linkButton}
                      onClick={() => setPanel({ kind: 'details', id: a.id })}
                      aria-label={`Ver detalhes de ${a.patient_name}`}
                    >
                      {a.patient_name}
                    </button>
                  ),
                },
                { key: 'specialty', header: 'Especialidade', render: (a) => a.specialty_name },
                { key: 'professional', header: 'Profissional', render: (a) => a.professional_name },
                {
                  key: 'status',
                  header: 'Status',
                  render: (a) => (
                    <Badge tone={APPOINTMENT_STATUS_TONES[a.status]}>{a.status_label}</Badge>
                  ),
                },
              ]}
            />
          )}
        </Card>
        <div className={grid.stack}>
          {selected && (
            <AppointmentDetails
              appointment={selected}
              busyStatus={busyStatus}
              canUpdate={hasAnyPermission(user, ['appointment.update'])}
              onChangeStatus={(status) => void changeStatus(selected, status)}
              onClose={() => setPanel({ kind: 'none' })}
            />
          )}
          {panel.kind === 'new' && (
            <NewAppointmentForm
              professionals={professionals}
              defaultDate={filters.date}
              onCreated={handleCreated}
              onClose={() => setPanel({ kind: 'none' })}
            />
          )}
          <AgendaSummaryCard appointments={appointments} />
        </div>
      </div>
    </>
  );
}

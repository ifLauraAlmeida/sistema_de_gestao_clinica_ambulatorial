import type { ReactElement, ReactNode } from 'react';
import { CalendarDays, CheckCircle2, Trash2, UserX, X } from 'lucide-react';
import { Badge } from '../../components/ui/Badge';
import { PhoneLink } from '../../components/ui/PhoneLink';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import type { Appointment, ManualAppointmentStatus } from '../../types/agenda';
import { formatLongDate, formatTime } from '../../utils/dateTime';
import { APPOINTMENT_STATUS_TONES, availableStatusChanges } from './agendaRules';
import styles from './AgendaPage.module.css';

const STATUS_ACTIONS: Record<
  ManualAppointmentStatus,
  { label: string; variant: 'primary' | 'secondary' | 'danger'; icon: ReactElement }
> = {
  AGENDADO: {
    label: 'Marcar como agendado',
    variant: 'secondary',
    icon: <CalendarDays size={16} />,
  },
  CONFIRMADO: { label: 'Confirmar', variant: 'primary', icon: <CheckCircle2 size={16} /> },
  NAO_COMPARECEU: { label: 'Não compareceu', variant: 'secondary', icon: <UserX size={16} /> },
  CANCELADO: { label: 'Cancelar', variant: 'danger', icon: <Trash2 size={16} /> },
};

interface AppointmentDetailsProps {
  appointment: Appointment;
  busyStatus: ManualAppointmentStatus | null;
  canUpdate: boolean;
  onChangeStatus: (status: ManualAppointmentStatus) => void;
  onClose: () => void;
}

/** Linhas exibidas só quando o serviço tem a opção (lateralidade, sedação, exames, preparo). */
function optionalRows(appointment: Appointment): [string, string][] {
  const rows: [string, string][] = [];
  if (appointment.laterality_label) rows.push(['Lateralidade', appointment.laterality_label]);
  if (appointment.with_sedation) rows.push(['Sedação', 'Sim']);
  if (appointment.laboratory_exam_names.length) {
    rows.push(['Exames', appointment.laboratory_exam_names.join(', ')]);
  }
  if (appointment.preparation) rows.push(['Preparo', appointment.preparation]);
  return rows;
}

export function AppointmentDetails({
  appointment,
  busyStatus,
  canUpdate,
  onChangeStatus,
  onClose,
}: AppointmentDetailsProps): ReactElement {
  const scheduledFor = new Date(appointment.scheduled_for);
  const rows: [string, ReactNode][] = [
    ['Telefone', <PhoneLink key="phone" phone={appointment.patient_phone} />],
    [
      'Data e horário',
      `${formatLongDate(scheduledFor)} às ${formatTime(appointment.scheduled_for)}`,
    ],
    ['Serviço', appointment.service_name ?? appointment.specialty_name],
    ...optionalRows(appointment),
    ['Profissional', appointment.professional_name],
    ['Senha', appointment.ticket_code ?? 'gerada no check-in'],
    ['Observações', appointment.notes || '—'],
  ];

  return (
    <Card
      title="Detalhes do agendamento"
      icon={<CalendarDays size={20} />}
      actions={
        <Button variant="ghost" icon={<X size={18} />} onClick={onClose}>
          Fechar
        </Button>
      }
    >
      <div className={styles.detailHeader}>
        <strong>{appointment.patient_name}</strong>
        <Badge tone={APPOINTMENT_STATUS_TONES[appointment.status]}>
          {appointment.status_label}
        </Badge>
      </div>
      <dl className={styles.detailList}>
        {rows.map(([term, description]) => (
          <div key={term} className={styles.detailRow}>
            <dt>{term}</dt>
            <dd>{description}</dd>
          </div>
        ))}
      </dl>
      {canUpdate && (
        <div className={styles.detailActions}>
          {availableStatusChanges(appointment.status).map((status) => (
            <Button
              key={status}
              variant={STATUS_ACTIONS[status].variant}
              icon={STATUS_ACTIONS[status].icon}
              isLoading={busyStatus === status}
              disabled={busyStatus !== null}
              onClick={() => onChangeStatus(status)}
            >
              {STATUS_ACTIONS[status].label}
            </Button>
          ))}
        </div>
      )}
    </Card>
  );
}

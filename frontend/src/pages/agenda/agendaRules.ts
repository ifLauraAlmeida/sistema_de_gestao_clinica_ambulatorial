import type { BadgeTone } from '../../components/ui/Badge';
import type { SelectOption } from '../../components/ui/SelectField';
import type {
  Appointment,
  AppointmentStatus,
  ManualAppointmentStatus,
  Professional,
} from '../../types/agenda';

export const APPOINTMENT_STATUS_TONES: Record<AppointmentStatus, BadgeTone> = {
  AGENDADO: 'info',
  CONFIRMADO: 'success',
  CHECK_IN_REALIZADO: 'warning',
  CANCELADO: 'neutral',
  NAO_COMPARECEU: 'danger',
};

export interface AgendaSummary {
  scheduled: number;
  confirmed: number;
  checkedIn: number;
  absentOrCancelled: number;
}

export function summarizeAgenda(appointments: Appointment[]): AgendaSummary {
  const count = (...statuses: AppointmentStatus[]): number =>
    appointments.filter((appointment) => statuses.includes(appointment.status)).length;
  return {
    scheduled: count('AGENDADO'),
    confirmed: count('CONFIRMADO'),
    checkedIn: count('CHECK_IN_REALIZADO'),
    absentOrCancelled: count('CANCELADO', 'NAO_COMPARECEU'),
  };
}

/**
 * Mudanças de status oferecidas na tela. É apenas conveniência de interface: o
 * backend valida os status permitidos à recepção.
 */
export function availableStatusChanges(status: AppointmentStatus): ManualAppointmentStatus[] {
  if (status === 'AGENDADO') return ['CONFIRMADO', 'NAO_COMPARECEU', 'CANCELADO'];
  if (status === 'CONFIRMADO') return ['NAO_COMPARECEU', 'CANCELADO'];
  return [];
}

export function professionalOptions(professionals: Professional[]): SelectOption[] {
  return professionals.map((professional) => ({
    value: professional.id,
    label: professional.name,
  }));
}

/** Especialidades sem repetição; filtradas pelo profissional quando informado. */
export function specialtyOptions(
  professionals: Professional[],
  professionalId?: string,
): SelectOption[] {
  const source = professionalId
    ? professionals.filter((professional) => professional.id === professionalId)
    : professionals;
  const unique = new Map<string, string>();
  source.flatMap((p) => p.specialties).forEach((s) => unique.set(s.id, s.name));
  return [...unique].map(([value, label]) => ({ value, label }));
}

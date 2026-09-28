export type AppointmentStatus =
  'AGENDADO' | 'CONFIRMADO' | 'CHECK_IN_REALIZADO' | 'CANCELADO' | 'NAO_COMPARECEU';

/** Status que a recepção pode definir manualmente (check-in tem fluxo próprio). */
export type ManualAppointmentStatus = Exclude<AppointmentStatus, 'CHECK_IN_REALIZADO'>;

export interface Appointment {
  id: string;
  patient: string;
  patient_name: string;
  professional: string;
  professional_name: string;
  specialty: string;
  specialty_name: string;
  scheduled_for: string;
  status: AppointmentStatus;
  status_label: string;
  notes: string;
  ticket_code: string | null;
}

export interface AgendaFilters {
  date: string;
  professional?: string;
  specialty?: string;
  search?: string;
}

export interface NewAppointmentInput {
  patient: string;
  professional: string;
  specialty: string;
  scheduled_for: string;
  notes: string;
}

export interface Specialty {
  id: string;
  name: string;
  ticket_prefix: string;
}

export interface Professional {
  id: string;
  name: string;
  specialties: Specialty[];
}

/** Atendimento criado no check-in (dados administrativos). */
export interface CheckInResult {
  id: string;
  ticket_code: string;
  patient_name: string;
  specialty_name: string;
  professional_name: string;
  status_label: string;
}

export type AppointmentStatus =
  'AGENDADO' | 'CONFIRMADO' | 'CHECK_IN_REALIZADO' | 'CANCELADO' | 'NAO_COMPARECEU';

/** Status que a recepção pode definir manualmente (check-in tem fluxo próprio). */
export type ManualAppointmentStatus = Exclude<AppointmentStatus, 'CHECK_IN_REALIZADO'>;

export interface Appointment {
  id: string;
  patient: string;
  patient_name: string;
  /** Contato para confirmar a consulta ou avisar o paciente. */
  patient_phone: string;
  professional: string;
  professional_name: string;
  specialty: string;
  specialty_name: string;
  scheduled_for: string;
  status: AppointmentStatus;
  status_label: string;
  notes: string;
  ticket_code: string | null;
  service: string | null;
  service_name: string | null;
  service_type_label: string | null;
  duration_minutes: number | null;
  laterality: Laterality | '';
  laterality_label: string;
  with_sedation: boolean;
  laboratory_exam_names: string[];
  /** Preparo do serviço combinado com o maior jejum dos exames. */
  preparation: string;
}

export interface AgendaFilters {
  date: string;
  professional?: string;
  specialty?: string;
  search?: string;
}

export type Laterality = 'DIREITA' | 'ESQUERDA' | 'BILATERAL';

export interface NewAppointmentInput {
  patient: string;
  professional: string;
  service: string;
  laterality: Laterality | '';
  with_sedation: boolean;
  laboratory_exams: string[];
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
  service_name: string | null;
  professional_name: string;
  status_label: string;
}

import type { Appointment } from '../types/agenda';
import type { QueueEntry } from '../types/queue';

/** Senha fictícia na fila. */
export function buildQueueEntry(overrides: Partial<QueueEntry> = {}): QueueEntry {
  return {
    id: 'entry-1',
    encounter_id: 'encounter-1',
    queue_type: 'CLINICAL',
    ticket_code: 'GINE01',
    patient_name: 'Paciente Fictício Alfa',
    specialty_name: 'Ginecologia',
    professional_name: 'Profissional Fictício',
    status: 'WAITING',
    status_label: 'Aguardando',
    encounter_status: 'AGUARDANDO_PROFISSIONAL',
    encounter_status_label: 'Aguardando profissional',
    entered_at: new Date().toISOString(),
    finished_at: null,
    last_call_destination: null,
    last_called_at: null,
    last_call_attempt: null,
    ...overrides,
  };
}

/** Agendamento fictício do dia. */
export function buildAppointment(overrides: Partial<Appointment> = {}): Appointment {
  return {
    id: 'appointment-1',
    patient: 'patient-1',
    patient_name: 'Paciente Fictício Alfa',
    professional: 'professional-1',
    professional_name: 'Profissional Fictício',
    specialty: 'specialty-1',
    specialty_name: 'Ginecologia',
    scheduled_for: new Date().toISOString(),
    status: 'AGENDADO',
    status_label: 'Agendado',
    notes: '',
    ticket_code: null,
    ...overrides,
  };
}

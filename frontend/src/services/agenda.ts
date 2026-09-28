import type {
  AgendaFilters,
  Appointment,
  CheckInResult,
  ManualAppointmentStatus,
  NewAppointmentInput,
  Professional,
} from '../types/agenda';
import { apiClient, withQuery } from './api';

export function listAgenda(filters: AgendaFilters): Promise<Appointment[]> {
  return apiClient.get(withQuery('/appointments/', { ...filters }));
}

export function createAppointment(input: NewAppointmentInput): Promise<Appointment> {
  return apiClient.post('/appointments/', input);
}

export function changeAppointmentStatus(
  appointmentId: string,
  status: ManualAppointmentStatus,
): Promise<Appointment> {
  return apiClient.patch(`/appointments/${appointmentId}/`, { status });
}

export function listProfessionals(): Promise<Professional[]> {
  return apiClient.get('/professionals/');
}

/** Confirma a chegada do paciente agendado; gera a senha e o coloca na fila da recepção. */
export function checkInAppointment(appointmentId: string): Promise<CheckInResult> {
  return apiClient.post('/check-ins/', { appointment_id: appointmentId });
}

import type { Appointment } from '../../types/agenda';

/** Agendamentos que ainda podem receber check-in (o backend também valida). */
export function canCheckIn(appointment: Appointment): boolean {
  return appointment.status === 'AGENDADO' || appointment.status === 'CONFIRMADO';
}

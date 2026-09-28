import type { AccessPermission, CurrentUser, UserRole } from '../types/auth';
import type { StationType, WorkSession } from '../types/workSession';

const ROLE_PERMISSIONS: Record<UserRole, AccessPermission[]> = {
  ATENDENTE: [
    'patient.create',
    'patient.view_demographics',
    'patient.update_demographics',
    'appointment.view',
    'appointment.create',
    'appointment.update',
    'checkin.create',
    'reception_queue.view',
    'reception_queue.call',
    'reception_queue.forward',
    'work_session.reception_desk',
  ],
  MEDICO: [
    'clinical_queue.view_own',
    'clinical_queue.view_inactive_own',
    'clinical_queue.call_own',
    'encounter.complete_own',
    'medical_record.view_active_patient',
    'work_session.consultation_room',
  ],
  GESTOR: [
    'patient.view_demographics',
    'appointment.view',
    'reception_queue.view',
    'clinical_queue.view_all',
    'audit.view',
    'work_session.reception_desk',
    'work_session.consultation_room',
  ],
};

const REQUIRED_STATION: Record<UserRole, StationType | null> = {
  ATENDENTE: 'RECEPTION_DESK',
  MEDICO: 'CONSULTATION_ROOM',
  GESTOR: null,
};

const ROLE_LABELS: Record<UserRole, string> = {
  ATENDENTE: 'Atendente',
  MEDICO: 'Médico',
  GESTOR: 'Gestor',
};

export function buildWorkSession(name: string, stationType: StationType): WorkSession {
  return {
    id: `session-${name}`,
    station: { id: `station-${name}`, name, station_type: stationType, station_type_label: '' },
    started_at: '2026-09-28T12:00:00Z',
    ended_at: null,
  };
}

/** Usuário fictício com as permissões do perfil. */
export function buildUser(role: UserRole, workSession: WorkSession | null = null): CurrentUser {
  return {
    id: `user-${role}`,
    username: `${role.toLowerCase()}.teste`,
    display_name: 'Ana Teste',
    role,
    role_label: ROLE_LABELS[role],
    permissions: ROLE_PERMISSIONS[role],
    required_station_type: REQUIRED_STATION[role],
    active_work_session: workSession,
  };
}

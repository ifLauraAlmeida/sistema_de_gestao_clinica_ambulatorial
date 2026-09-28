import type { WorkSession, StationType } from './workSession';

export type UserRole = 'ATENDENTE' | 'MEDICO' | 'GESTOR';

/** Permissões granulares definidas no backend (apps/accounts/access_permissions.py). */
export type AccessPermission =
  | 'patient.create'
  | 'patient.view_demographics'
  | 'patient.update_demographics'
  | 'appointment.view'
  | 'appointment.create'
  | 'appointment.update'
  | 'checkin.create'
  | 'reception_queue.view'
  | 'reception_queue.call'
  | 'reception_queue.forward'
  | 'clinical_queue.view_own'
  | 'clinical_queue.view_inactive_own'
  | 'clinical_queue.call_own'
  | 'clinical_queue.view_all'
  | 'clinical_queue.call_any'
  | 'encounter.complete_own'
  | 'medical_record.view_active_patient'
  | 'medical_record.update_active_patient'
  | 'medical_record.view_any'
  | 'billing.view_history'
  | 'reports.view_own'
  | 'reports.view_all'
  | 'users.manage'
  | 'audit.view'
  | 'work_session.reception_desk'
  | 'work_session.consultation_room';

/**
 * Usuário autenticado conforme `/api/v1/auth/me/`.
 *
 * As permissões servem apenas para montar a interface; a autorização real é
 * sempre verificada pelo backend.
 */
export interface CurrentUser {
  id: string;
  username: string;
  display_name: string;
  role: UserRole;
  role_label: string;
  permissions: AccessPermission[];
  required_station_type: StationType | null;
  active_work_session: WorkSession | null;
}

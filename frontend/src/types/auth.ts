import type { WorkSession, StationType } from './workSession';

export type UserRole = 'ATENDENTE' | 'MEDICO' | 'PROFISSIONAL_SAUDE' | 'TECNICO' | 'GESTOR';

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
  | 'encounter.start_own'
  | 'encounter.complete_own'
  | 'medical_record.view_active_patient'
  | 'medical_record.update_active_patient'
  | 'medical_record.view_any'
  | 'procedure_record.update_own'
  | 'procedure_record.view_any'
  | 'catalog.view'
  | 'billing.view_history'
  | 'billing.manage'
  | 'reports.view_own'
  | 'reports.view_all'
  | 'users.manage'
  | 'audit.view'
  | 'work_session.reception_desk'
  | 'work_session.consultation_room'
  | 'work_session.exam_room';

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

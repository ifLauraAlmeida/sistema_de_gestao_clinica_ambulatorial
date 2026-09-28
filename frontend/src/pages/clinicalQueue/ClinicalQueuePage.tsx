import type { ReactElement } from 'react';
import { useCurrentUser } from '../../hooks/useAuth';
import { hasAnyPermission } from '../../utils/userAccess';
import { DoctorClinicalQueue } from './DoctorClinicalQueue';
import { ManagerClinicalQueue } from './ManagerClinicalQueue';

/** Fila clínica: visão geral para quem vê todas as filas; própria fila para o médico. */
export function ClinicalQueuePage(): ReactElement {
  const user = useCurrentUser();
  if (hasAnyPermission(user, ['clinical_queue.view_all'])) return <ManagerClinicalQueue />;
  return <DoctorClinicalQueue />;
}

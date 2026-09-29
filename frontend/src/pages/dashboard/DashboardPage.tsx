import type { ReactElement } from 'react';
import { useCurrentUser } from '../../hooks/useAuth';
import { hasAnyPermission } from '../../utils/userAccess';
import { DoctorDashboard } from './DoctorDashboard';
import { ManagerDashboard } from './ManagerDashboard';
import { ReceptionDashboard } from './ReceptionDashboard';

/** Dashboard inicial; o conteúdo varia conforme o perfil do usuário. */
export function DashboardPage(): ReactElement {
  const user = useCurrentUser();
  if (hasAnyPermission(user, ['clinical_queue.view_all'])) return <ManagerDashboard />;
  // Médico, profissional de saúde e técnico: resumo da própria fila.
  if (hasAnyPermission(user, ['clinical_queue.view_own'])) return <DoctorDashboard />;
  return <ReceptionDashboard />;
}

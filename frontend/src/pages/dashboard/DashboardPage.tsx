import type { ReactElement } from 'react';
import { useCurrentUser } from '../../hooks/useAuth';
import { DoctorDashboard } from './DoctorDashboard';
import { ManagerDashboard } from './ManagerDashboard';
import { ReceptionDashboard } from './ReceptionDashboard';

/** Dashboard inicial; o conteúdo varia conforme o perfil do usuário. */
export function DashboardPage(): ReactElement {
  const { role } = useCurrentUser();
  if (role === 'MEDICO') return <DoctorDashboard />;
  if (role === 'GESTOR') return <ManagerDashboard />;
  return <ReceptionDashboard />;
}

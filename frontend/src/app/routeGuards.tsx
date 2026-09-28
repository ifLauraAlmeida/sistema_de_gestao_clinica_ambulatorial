import type { ReactElement } from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { Loading } from '../components/ui/Loading';
import { useAuth, useCurrentUser } from '../hooks/useAuth';
import type { AccessPermission } from '../types/auth';
import { hasAnyPermission, needsWorkstationSelection } from '../utils/userAccess';
import { AccessDeniedPage } from '../pages/AccessDeniedPage';

/** Exige sessão autenticada; caso contrário envia ao login. */
export function RequireAuthentication(): ReactElement {
  const { status } = useAuth();
  const location = useLocation();

  if (status === 'loading') return <Loading fullScreen label="Verificando sessão…" />;
  if (status === 'anonymous') return <Navigate to="/login" replace state={{ from: location }} />;
  return <Outlet />;
}

/** Atendente e médico precisam informar guichê/consultório antes de operar. */
export function RequireWorkstation(): ReactElement {
  const user = useCurrentUser();
  if (needsWorkstationSelection(user)) return <Navigate to="/workstation" replace />;
  return <Outlet />;
}

/** Oculta telas sem permissão. A API também nega essas operações. */
export function RequirePermission({ anyOf }: { anyOf: AccessPermission[] }): ReactElement {
  const user = useCurrentUser();
  if (anyOf.length > 0 && !hasAnyPermission(user, anyOf)) return <AccessDeniedPage />;
  return <Outlet />;
}

/** Usuário já autenticado não volta para a tela de login. */
export function RedirectIfAuthenticated(): ReactElement {
  const { status } = useAuth();
  if (status === 'loading') return <Loading fullScreen label="Verificando sessão…" />;
  if (status === 'authenticated') return <Navigate to="/dashboard" replace />;
  return <Outlet />;
}

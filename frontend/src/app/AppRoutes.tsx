import type { ReactElement } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import { MainLayout } from '../layouts/MainLayout';
import { DashboardPage } from '../pages/dashboard/DashboardPage';
import { LoginPage } from '../pages/login/LoginPage';
import { ModulePlaceholderPage } from '../pages/ModulePlaceholderPage';
import { NotFoundPage } from '../pages/NotFoundPage';
import { WorkstationPage } from '../pages/workstation/WorkstationPage';
import { NAVIGATION_ITEMS } from './navigation';
import {
  RedirectIfAuthenticated,
  RequireAuthentication,
  RequirePermission,
  RequireWorkstation,
} from './routeGuards';

const PLACEHOLDER_DESCRIPTIONS: Record<string, string> = {
  '/pacientes': 'Cadastro e busca de pacientes.',
  '/agenda': 'Agendamento de consultas e acompanhamento.',
  '/check-in': 'Registro de chegada e confirmação do paciente.',
  '/fila-recepcao': 'Fila completa da recepção e chamadas.',
  '/fila-clinica': 'Fila clínica e prontuário do atendimento.',
  '/auditoria': 'Consulta dos eventos de auditoria.',
};

/**
 * Fluxo: não autenticado → login; atendente/médico sem posto → seleção de
 * guichê/consultório; demais → dashboard.
 */
export function AppRoutes(): ReactElement {
  return (
    <Routes>
      <Route element={<RedirectIfAuthenticated />}>
        <Route path="/login" element={<LoginPage />} />
      </Route>
      <Route element={<RequireAuthentication />}>
        <Route path="/workstation" element={<WorkstationPage />} />
        <Route element={<RequireWorkstation />}>
          <Route element={<MainLayout />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            {NAVIGATION_ITEMS.filter((item) => item.path in PLACEHOLDER_DESCRIPTIONS).map(
              (item) => (
                <Route key={item.path} element={<RequirePermission anyOf={item.anyOf} />}>
                  <Route
                    path={item.path}
                    element={
                      <ModulePlaceholderPage
                        title={item.label}
                        description={PLACEHOLDER_DESCRIPTIONS[item.path] ?? ''}
                      />
                    }
                  />
                </Route>
              ),
            )}
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Route>
      </Route>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

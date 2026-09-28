import type { ReactElement } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import { MainLayout } from '../layouts/MainLayout';
import { AgendaPage } from '../pages/agenda/AgendaPage';
import { CheckInPage } from '../pages/checkIn/CheckInPage';
import { ClinicalQueuePage } from '../pages/clinicalQueue/ClinicalQueuePage';
import { DashboardPage } from '../pages/dashboard/DashboardPage';
import { EncounterPage } from '../pages/encounter/EncounterPage';
import { PatientsPage } from '../pages/patients/PatientsPage';
import { ReceptionQueuePage } from '../pages/receptionQueue/ReceptionQueuePage';
import { LoginPage } from '../pages/login/LoginPage';
import { ModulePlaceholderPage } from '../pages/ModulePlaceholderPage';
import { NotFoundPage } from '../pages/NotFoundPage';
import { WorkstationPage } from '../pages/workstation/WorkstationPage';
import { NAVIGATION_ITEMS, type NavigationItem } from './navigation';
import {
  RedirectIfAuthenticated,
  RequireAuthentication,
  RequirePermission,
  RequireWorkstation,
} from './routeGuards';

/** Páginas já implementadas, por caminho do menu. */
const MODULE_PAGES: Record<string, ReactElement> = {
  '/pacientes': <PatientsPage />,
  '/agenda': <AgendaPage />,
  '/check-in': <CheckInPage />,
  '/fila-recepcao': <ReceptionQueuePage />,
  '/fila-clinica': <ClinicalQueuePage />,
};

const PLACEHOLDER_DESCRIPTIONS: Record<string, string> = {
  '/auditoria': 'Consulta dos eventos de auditoria.',
};

/** Página do módulo, ou tela reservada quando o módulo ainda não foi implementado. */
function moduleElementFor(item: NavigationItem): ReactElement {
  return (
    MODULE_PAGES[item.path] ?? (
      <ModulePlaceholderPage
        title={item.label}
        description={PLACEHOLDER_DESCRIPTIONS[item.path] ?? ''}
      />
    )
  );
}

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
            {NAVIGATION_ITEMS.filter((item) => item.path !== '/dashboard').map((item) => (
              <Route key={item.path} element={<RequirePermission anyOf={item.anyOf} />}>
                <Route path={item.path} element={moduleElementFor(item)} />
              </Route>
            ))}
            <Route
              element={
                <RequirePermission
                  anyOf={['medical_record.view_active_patient', 'medical_record.view_any']}
                />
              }
            >
              <Route path="/atendimento/:encounterId" element={<EncounterPage />} />
            </Route>
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Route>
      </Route>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

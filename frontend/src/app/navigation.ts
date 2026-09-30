import {
  CalendarDays,
  BookOpen,
  ClipboardCheck,
  CreditCard,
  LayoutDashboard,
  ListOrdered,
  ShieldCheck,
  Stethoscope,
  Users,
  type LucideIcon,
} from 'lucide-react';
import type { AccessPermission, CurrentUser } from '../types/auth';
import { hasAnyPermission } from '../utils/userAccess';

export interface NavigationItem {
  label: string;
  path: string;
  icon: LucideIcon;
  /** Qualquer uma destas permissões exibe o item. Vazio: todos os perfis. */
  anyOf: AccessPermission[];
}

/**
 * Menu principal. A visibilidade segue as permissões do backend, mas ocultar um
 * item NÃO é segurança: a API nega acessos indevidos independentemente do menu.
 */
export const NAVIGATION_ITEMS: NavigationItem[] = [
  { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard, anyOf: [] },
  { label: 'Pacientes', path: '/pacientes', icon: Users, anyOf: ['patient.view_demographics'] },
  { label: 'Agenda', path: '/agenda', icon: CalendarDays, anyOf: ['appointment.view'] },
  { label: 'Check-in', path: '/check-in', icon: ClipboardCheck, anyOf: ['checkin.create'] },
  {
    label: 'Fila da recepção',
    path: '/fila-recepcao',
    icon: ListOrdered,
    anyOf: ['reception_queue.view'],
  },
  {
    label: 'Fila clínica',
    path: '/fila-clinica',
    icon: Stethoscope,
    anyOf: ['clinical_queue.view_own', 'clinical_queue.view_all'],
  },
  { label: 'Catálogo de serviços', path: '/catalogo', icon: BookOpen, anyOf: ['catalog.view'] },
  {
    label: 'Financeiro e Autorizações',
    path: '/financeiro',
    icon: CreditCard,
    anyOf: ['billing.view_history'],
  },
  { label: 'Auditoria', path: '/auditoria', icon: ShieldCheck, anyOf: ['audit.view'] },
];

export function getVisibleNavigationItems(user: CurrentUser): NavigationItem[] {
  return NAVIGATION_ITEMS.filter(
    (item) => item.anyOf.length === 0 || hasAnyPermission(user, item.anyOf),
  );
}

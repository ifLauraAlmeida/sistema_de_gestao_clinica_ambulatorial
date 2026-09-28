import type { AccessPermission, CurrentUser } from '../types/auth';

/**
 * Indica se o usuário possui ao menos uma das permissões.
 *
 * Usado apenas para decidir o que exibir: o backend continua validando cada
 * requisição.
 */
export function hasAnyPermission(user: CurrentUser, permissions: AccessPermission[]): boolean {
  return permissions.some((permission) => user.permissions.includes(permission));
}

/** Perfis com posto obrigatório (atendente/médico) precisam selecioná-lo antes de operar. */
export function needsWorkstationSelection(user: CurrentUser): boolean {
  return user.required_station_type !== null && user.active_work_session === null;
}

/** Primeiro nome para saudações ("Olá, Ana!"). */
export function firstNameOf(user: CurrentUser): string {
  return user.display_name.split(' ')[0] ?? user.display_name;
}

/** Iniciais exibidas no avatar da barra superior. */
export function initialsOf(user: CurrentUser): string {
  const parts = user.display_name.split(' ').filter(Boolean);
  const initials =
    parts.length > 1 ? `${parts[0]?.[0]}${parts.at(-1)?.[0]}` : parts[0]?.slice(0, 2);
  return (initials ?? '?').toUpperCase();
}

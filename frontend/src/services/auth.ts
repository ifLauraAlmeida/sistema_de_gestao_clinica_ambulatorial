import type { CurrentUser } from '../types/auth';
import { ApiError, apiClient } from './api';

/** Autentica por sessão/cookie; retorna o usuário autenticado. */
export function login(username: string, password: string): Promise<CurrentUser> {
  return apiClient.post<CurrentUser>('/auth/login/', { username, password });
}

export async function logout(): Promise<void> {
  await apiClient.post<undefined>('/auth/logout/');
}

/** Retorna o usuário da sessão atual, ou `null` quando não há sessão. */
export async function fetchCurrentUser(): Promise<CurrentUser | null> {
  try {
    return await apiClient.get<CurrentUser>('/auth/me/');
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) return null;
    throw error;
  }
}

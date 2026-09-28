import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactElement,
  type ReactNode,
} from 'react';
import { fetchCurrentUser, login, logout } from '../services/auth';
import type { CurrentUser } from '../types/auth';
import { AuthContext, type AuthContextValue, type AuthStatus } from './authContext';

/**
 * Mantém o usuário da sessão Django em memória.
 *
 * Nenhuma credencial ou token é guardado em localStorage: a sessão vive no
 * cookie HttpOnly definido pelo backend.
 */
export function AuthProvider({ children }: { children: ReactNode }): ReactElement {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [status, setStatus] = useState<AuthStatus>('loading');

  const applyUser = useCallback((nextUser: CurrentUser | null): CurrentUser | null => {
    setUser(nextUser);
    setStatus(nextUser ? 'authenticated' : 'anonymous');
    return nextUser;
  }, []);

  const refreshUser = useCallback(
    async (): Promise<CurrentUser | null> => applyUser(await fetchCurrentUser()),
    [applyUser],
  );

  useEffect(() => {
    let isActive = true;
    fetchCurrentUser().then(
      (currentUser) => isActive && applyUser(currentUser),
      () => isActive && applyUser(null),
    );
    return () => {
      isActive = false;
    };
  }, [applyUser]);

  const signIn = useCallback(
    async (username: string, password: string): Promise<CurrentUser> => {
      const authenticated = await login(username, password);
      applyUser(authenticated);
      return authenticated;
    },
    [applyUser],
  );

  const signOut = useCallback(async (): Promise<void> => {
    try {
      await logout();
    } finally {
      applyUser(null);
    }
  }, [applyUser]);

  const value = useMemo<AuthContextValue>(
    () => ({ status, user, signIn, signOut, refreshUser }),
    [status, user, signIn, signOut, refreshUser],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

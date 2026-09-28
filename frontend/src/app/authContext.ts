import { createContext } from 'react';
import type { CurrentUser } from '../types/auth';

export type AuthStatus = 'loading' | 'authenticated' | 'anonymous';

export interface AuthContextValue {
  status: AuthStatus;
  user: CurrentUser | null;
  signIn: (username: string, password: string) => Promise<CurrentUser>;
  signOut: () => Promise<void>;
  refreshUser: () => Promise<CurrentUser | null>;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

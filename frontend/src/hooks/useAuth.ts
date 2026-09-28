import { useContext } from 'react';
import { AuthContext, type AuthContextValue } from '../app/authContext';

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth precisa ser usado dentro de <AuthProvider>.');
  }
  return context;
}

/** Usuário autenticado; só deve ser usado em rotas protegidas. */
export function useCurrentUser(): NonNullable<AuthContextValue['user']> {
  const { user } = useAuth();
  if (!user) {
    throw new Error('useCurrentUser exige usuário autenticado (rota protegida).');
  }
  return user;
}

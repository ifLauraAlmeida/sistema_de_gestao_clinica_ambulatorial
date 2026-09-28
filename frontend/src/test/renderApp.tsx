import { render, type RenderResult } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AppRoutes } from '../app/AppRoutes';
import { AuthProvider } from '../app/AuthProvider';

/** Renderiza a aplicação completa em uma rota inicial, sem navegador real. */
export function renderApp(initialPath: string): RenderResult {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </MemoryRouter>,
  );
}

import '@testing-library/jest-dom/vitest';
import { cleanup, configure } from '@testing-library/react';
import { afterEach } from 'vitest';

// Buscas assíncronas (findBy/waitFor) com folga para máquinas carregadas e CI;
// o padrão de 1 s gerava falhas intermitentes sem erro real.
configure({ asyncUtilTimeout: 3000 });

afterEach(() => {
  cleanup();
});

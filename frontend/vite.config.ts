/// <reference types="vitest/config" />
import react from '@vitejs/plugin-react';
import { defineConfig, loadEnv } from 'vite';

// Em desenvolvimento o Vite encaminha /api para o Django. Para o navegador,
// frontend e API ficam na mesma origem, e o cookie de sessão/CSRF funciona sem
// CORS. Em produção o proxy reverso (Nginx) faz o mesmo papel.
export default defineConfig(({ mode }) => {
  const env = { ...loadEnv(mode, '..', 'VITE_'), ...process.env };
  const backendUrl = env.VITE_BACKEND_URL ?? 'http://localhost:8000';

  return {
    plugins: [react()],
    server: {
      host: '0.0.0.0',
      port: 5173,
      proxy: {
        '/api': { target: backendUrl, changeOrigin: false },
        '/ws': { target: backendUrl.replace(/^http/, 'ws'), ws: true },
      },
    },
    test: {
      environment: 'jsdom',
      globals: true,
      setupFiles: ['./src/test/setup.ts'],
      testTimeout: 15_000,
      css: false,
    },
  };
});

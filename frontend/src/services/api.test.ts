import { afterEach, describe, expect, it, vi } from 'vitest';
import { FakeBackend } from '../test/FakeBackend';
import { ApiError, apiClient } from './api';

describe('apiClient', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    document.cookie = 'csrftoken=; expires=Thu, 01 Jan 1970 00:00:00 GMT';
  });

  it('envia o token CSRF do cookie em requisições de escrita', async () => {
    document.cookie = 'csrftoken=token-de-teste';
    const backend = new FakeBackend().on('POST', '/api/v1/auth/logout/', () => ({ status: 204 }));
    backend.install();

    await apiClient.post<undefined>('/auth/logout/');

    const [request] = backend.requestsTo('POST', '/api/v1/auth/logout/');
    expect(request?.headers['X-CSRFToken']).toBe('token-de-teste');
  });

  it('converte o formato padronizado de erro em ApiError', async () => {
    new FakeBackend()
      .on('GET', '/api/v1/clinical-queue/', () => ({
        status: 403,
        body: { error: { code: 'permission_denied', message: 'Sem permissão.' } },
      }))
      .install();

    const request = apiClient.get('/clinical-queue/');

    await expect(request).rejects.toBeInstanceOf(ApiError);
    await expect(request).rejects.toMatchObject({ status: 403, code: 'permission_denied' });
  });
});

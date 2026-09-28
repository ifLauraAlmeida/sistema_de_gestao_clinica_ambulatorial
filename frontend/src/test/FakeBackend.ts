import { vi } from 'vitest';

type RouteHandler = (body: unknown) => { status: number; body?: unknown };

export interface RecordedRequest {
  method: string;
  path: string;
  headers: Record<string, string>;
  body: unknown;
}

/**
 * Backend simulado para testes: substitui `fetch` e responde por método + caminho.
 *
 * Exemplo:
 *   const backend = new FakeBackend().on('GET', '/api/v1/auth/me/', () => ({ status: 401 }));
 *   backend.install();
 */
export class FakeBackend {
  readonly requests: RecordedRequest[] = [];
  private readonly routes = new Map<string, RouteHandler>();

  on(method: string, path: string, handler: RouteHandler): this {
    this.routes.set(`${method} ${path}`, handler);
    return this;
  }

  install(): void {
    vi.stubGlobal(
      'fetch',
      vi.fn((input: string, init?: RequestInit) => this.handle(input, init)),
    );
  }

  requestsTo(method: string, path: string): RecordedRequest[] {
    return this.requests.filter((request) => request.method === method && request.path === path);
  }

  private async handle(path: string, init: RequestInit = {}): Promise<Response> {
    const method = init.method ?? 'GET';
    const body: unknown = typeof init.body === 'string' ? JSON.parse(init.body) : undefined;
    const headers = { ...(init.headers as Record<string, string> | undefined) };
    this.requests.push({ method, path, headers, body });

    const handler = this.routes.get(`${method} ${path}`);
    const result = handler ? handler(body) : { status: 404, body: notFoundBody(path) };
    const payload = result.body === undefined ? null : JSON.stringify(result.body);
    return new Response(payload, {
      status: result.status,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}

function notFoundBody(path: string): unknown {
  return { error: { code: 'not_found', message: `Rota não simulada: ${path}` } };
}

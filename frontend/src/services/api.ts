import type { ApiErrorBody } from '../types/api';

const API_BASE_PATH = '/api/v1';
const CSRF_COOKIE_NAME = 'csrftoken';
const UNSAFE_METHODS = new Set(['POST', 'PUT', 'PATCH', 'DELETE']);

type HttpMethod = 'GET' | 'POST' | 'PATCH' | 'PUT';

/** Erro retornado pela API no formato `{ error: { code, message } }`. */
export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly details?: Record<string, string[]>;

  constructor(status: number, code: string, message: string, details?: Record<string, string[]>) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

/** Lê o token CSRF do cookie definido pelo Django. */
export function readCsrfToken(): string | null {
  const match = document.cookie
    .split(';')
    .map((part) => part.trim())
    .find((part) => part.startsWith(`${CSRF_COOKIE_NAME}=`));
  return match ? decodeURIComponent(match.slice(CSRF_COOKIE_NAME.length + 1)) : null;
}

/** Garante que o cookie CSRF exista antes de requisições de escrita. */
export async function ensureCsrfCookie(): Promise<void> {
  if (readCsrfToken()) return;
  await fetch(`${API_BASE_PATH}/auth/csrf/`, { credentials: 'same-origin' });
}

async function buildHeaders(method: HttpMethod, hasBody: boolean): Promise<HeadersInit> {
  const headers: Record<string, string> = { Accept: 'application/json' };
  if (hasBody) headers['Content-Type'] = 'application/json';
  if (UNSAFE_METHODS.has(method)) {
    await ensureCsrfCookie();
    const token = readCsrfToken();
    if (token) headers['X-CSRFToken'] = token;
  }
  return headers;
}

async function toApiError(response: Response): Promise<ApiError> {
  const body = (await response.json().catch(() => null)) as ApiErrorBody | null;
  if (body?.error) {
    return new ApiError(response.status, body.error.code, body.error.message, body.error.details);
  }
  return new ApiError(
    response.status,
    'unexpected_response',
    'Falha na comunicação com o servidor.',
  );
}

async function request<T>(method: HttpMethod, path: string, body?: unknown): Promise<T> {
  const hasBody = body !== undefined;
  const response = await fetch(`${API_BASE_PATH}${path}`, {
    method,
    credentials: 'same-origin',
    headers: await buildHeaders(method, hasBody),
    body: hasBody ? JSON.stringify(body) : undefined,
  });
  if (!response.ok) throw await toApiError(response);
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

/**
 * Único ponto de comunicação HTTP com o backend.
 *
 * Exemplo:
 *   const user = await apiClient.get<CurrentUser>('/auth/me/');
 */
export const apiClient = {
  get: <T>(path: string): Promise<T> => request<T>('GET', path),
  post: <T>(path: string, body?: unknown): Promise<T> => request<T>('POST', path, body),
  patch: <T>(path: string, body?: unknown): Promise<T> => request<T>('PATCH', path, body),
  put: <T>(path: string, body?: unknown): Promise<T> => request<T>('PUT', path, body),
};

/**
 * Anexa parâmetros de consulta ao caminho, ignorando valores vazios.
 *
 * Exemplo:
 *   withQuery('/appointments/', { date: '2026-09-28', search: '' }) // '/appointments/?date=2026-09-28'
 */
export function withQuery(
  path: string,
  params: Record<string, string | number | undefined>,
): string {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== '') query.set(key, String(value));
  }
  const text = query.toString();
  return text ? `${path}?${text}` : path;
}

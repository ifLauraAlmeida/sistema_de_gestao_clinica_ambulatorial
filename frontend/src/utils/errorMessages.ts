import { ApiError } from '../services/api';

/** Mensagem exibível para qualquer erro; nunca expõe detalhes internos. */
export function describeError(error: unknown, fallback: string): string {
  if (error instanceof ApiError && error.status < 500) return error.message;
  return fallback;
}

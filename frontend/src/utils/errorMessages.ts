import { ApiError } from '../services/api';

/** Mensagem exibível para qualquer erro; nunca expõe detalhes internos. */
export function describeError(error: unknown, fallback: string): string {
  if (error instanceof ApiError && error.status < 500) return error.message;
  return fallback;
}

/**
 * Erros de validação por campo retornados pela API (`error.details`).
 *
 * Exemplo:
 *   fieldErrorsOf(error).cpf // "CPF inválido: ..."
 */
export function fieldErrorsOf(error: unknown): Record<string, string> {
  if (!(error instanceof ApiError) || !error.details) return {};
  return Object.fromEntries(
    Object.entries(error.details).map(([field, messages]) => [field, messages.join(' ')]),
  );
}

/** Corpo padronizado de erro da API (apps/core/api_errors.py). */
export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    details?: Record<string, string[]>;
  };
}

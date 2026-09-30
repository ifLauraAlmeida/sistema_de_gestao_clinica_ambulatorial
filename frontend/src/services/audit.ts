import type { AuditEvent, AuditQuery, AuditSummary } from '../types/audit';
import type { Paginated } from '../types/pagination';
import { apiClient, withQuery } from './api';

const API_BASE_PATH = '/api/v1';

export function listAuditEvents(query: AuditQuery): Promise<Paginated<AuditEvent>> {
  return apiClient.get(withQuery('/audit/events/', { ...query }));
}

/** Indicadores e opções de filtro. Abrir a auditoria também gera evento no backend. */
export function getAuditSummary(): Promise<AuditSummary> {
  return apiClient.get('/audit/summary/');
}

/** Endereço do CSV com os mesmos filtros (download pela sessão atual; é auditado). */
export function auditExportUrl(query: AuditQuery): string {
  return `${API_BASE_PATH}${withQuery('/audit/events/export/', { ...query, page: undefined })}`;
}

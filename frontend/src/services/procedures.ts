import type { ProcedureValue, ProcedureView } from '../types/procedure';
import { apiClient } from './api';

/** Autorizado ao responsável enquanto o atendimento está na fila ativa (e ao gestor, só leitura). */
export function getProcedure(encounterId: string): Promise<ProcedureView> {
  return apiClient.get(`/encounters/${encounterId}/procedure/`);
}

/** Grava nova versão dos campos do procedimento. */
export function saveProcedure(
  encounterId: string,
  values: Record<string, ProcedureValue>,
): Promise<ProcedureView> {
  return apiClient.put(`/encounters/${encounterId}/procedure/`, { values });
}

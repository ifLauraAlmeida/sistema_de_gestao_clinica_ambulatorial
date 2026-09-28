import type { ClinicalQueueView, QueueCall, QueueEntry } from '../types/queue';
import { apiClient, withQuery } from './api';

export function listReceptionQueue(): Promise<QueueEntry[]> {
  return apiClient.get<QueueEntry[]>('/reception-queue/');
}

export function listRecentReceptionCalls(): Promise<QueueCall[]> {
  return apiClient.get<QueueCall[]>('/reception-queue/calls/');
}

/** Chama (ou rechama) a senha para o guichê da sessão de trabalho atual. */
export function callReceptionTicket(entryId: string): Promise<QueueCall> {
  return apiClient.post<QueueCall>(`/reception-queue/${entryId}/call/`);
}

export async function forwardToClinicalQueue(entryId: string): Promise<void> {
  await apiClient.post<undefined>(`/reception-queue/${entryId}/forward/`);
}

/**
 * Fila clínica ativa ou inativa. `professionalId` só é aceito pelo backend para
 * quem pode ver todas as filas (gestor); médicos recebem apenas a própria.
 */
export function listClinicalQueue(
  view: ClinicalQueueView,
  professionalId?: string,
): Promise<QueueEntry[]> {
  return apiClient.get<QueueEntry[]>(
    withQuery('/clinical-queue/', { status: view, professional_id: professionalId }),
  );
}

/** Chama (ou rechama) a senha para o consultório da sessão de trabalho atual. */
export function callClinicalTicket(entryId: string): Promise<QueueCall> {
  return apiClient.post<QueueCall>(`/clinical-queue/${entryId}/call/`);
}

/** Registra que o paciente chamado entrou no consultório (EM_ATENDIMENTO). */
export async function startEncounter(encounterId: string): Promise<void> {
  await apiClient.post<undefined>(`/encounters/${encounterId}/start/`);
}

/** Marca o atendimento como ATENDIDO. */
export async function completeEncounter(encounterId: string): Promise<void> {
  await apiClient.post<undefined>(`/encounters/${encounterId}/complete/`);
}

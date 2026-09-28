import type { ClinicalQueueView, QueueCall, QueueEntry } from '../types/queue';
import { apiClient } from './api';

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

export function listClinicalQueue(view: ClinicalQueueView): Promise<QueueEntry[]> {
  return apiClient.get<QueueEntry[]>(`/clinical-queue/?status=${view}`);
}

/** Chama (ou rechama) a senha para o consultório da sessão de trabalho atual. */
export function callClinicalTicket(entryId: string): Promise<QueueCall> {
  return apiClient.post<QueueCall>(`/clinical-queue/${entryId}/call/`);
}

/** Marca o atendimento como ATENDIDO. */
export async function completeEncounter(encounterId: string): Promise<void> {
  await apiClient.post<undefined>(`/encounters/${encounterId}/complete/`);
}

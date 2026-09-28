import type { ClinicalNote, HistoryEncounter, MedicalRecord } from '../types/medicalRecord';
import { apiClient } from './api';

/**
 * Prontuário via atendimento. O backend só autoriza enquanto o atendimento
 * está na fila ativa do médico (ou para o gestor), e audita cada acesso.
 */
export function getMedicalRecord(encounterId: string): Promise<MedicalRecord> {
  return apiClient.get(`/encounters/${encounterId}/medical-record/`);
}

export function getClinicalHistory(encounterId: string): Promise<HistoryEncounter[]> {
  return apiClient.get(`/encounters/${encounterId}/clinical-history/`);
}

export function createClinicalNote(encounterId: string, content: string): Promise<ClinicalNote> {
  return apiClient.post(`/encounters/${encounterId}/clinical-notes/`, { content });
}

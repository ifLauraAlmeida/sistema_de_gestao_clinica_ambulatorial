import type { EncounterStatus } from './queue';

export interface EncounterSummary {
  id: string;
  ticket_code: string;
  service_date: string;
  patient_name: string;
  professional_name: string;
  specialty_name: string;
  status: EncounterStatus;
  status_label: string;
  checked_in_at: string;
  completed_at: string | null;
  service_name: string | null;
  laterality_label: string;
  with_sedation: boolean;
}

export interface PatientSummary {
  id: string;
  display_name: string;
  full_name: string;
  birth_date: string;
  age: number;
}

export interface ClinicalNote {
  id: string;
  content: string;
  author_name: string;
  created_at: string;
}

/** Prontuário no contexto de um atendimento autorizado. */
export interface MedicalRecord {
  encounter: EncounterSummary;
  patient: PatientSummary;
  clinical_notes: ClinicalNote[];
}

/** Atendimento anterior na linha do tempo clínica. */
export interface HistoryEncounter {
  id: string;
  service_date: string;
  specialty_name: string;
  professional_name: string;
  clinical_notes: ClinicalNote[];
}

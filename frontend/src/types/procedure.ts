import type { EncounterSummary, PatientSummary } from './medicalRecord';

export type FormFieldType = 'TEXT' | 'TEXTAREA' | 'NUMBER' | 'BOOLEAN' | 'SELECT' | 'TIME';

export interface ExecutionFormField {
  key: string;
  label: string;
  field_type: FormFieldType;
  unit: string;
  options: string[];
  is_required: boolean;
}

export type ProcedureValue = string | number | boolean | null;

/** O que realizar no atendimento e os campos do procedimento (sem prontuário). */
export interface ProcedureView {
  encounter: EncounterSummary;
  patient: PatientSummary;
  service_type_label: string | null;
  preparation: string;
  laboratory_exams: { name: string; sample_type_label: string }[];
  form: { name: string; fields: ExecutionFormField[] } | null;
  values: Record<string, ProcedureValue> | null;
  recorded_at: string | null;
  recorded_by_name: string | null;
  can_edit: boolean;
}

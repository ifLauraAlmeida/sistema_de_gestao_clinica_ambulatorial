export type QueueType = 'RECEPTION' | 'CLINICAL';

export type QueueEntryStatus = 'WAITING' | 'CALLED' | 'FINISHED' | 'CANCELLED' | 'NO_SHOW';

export type EncounterStatus =
  | 'CHECK_IN_REALIZADO'
  | 'AGUARDANDO_PROFISSIONAL'
  | 'CHAMADO'
  | 'EM_ATENDIMENTO'
  | 'ATENDIDO'
  | 'NAO_COMPARECEU'
  | 'CANCELADO';

/** Senha na fila, com dados administrativos (sem conteúdo clínico). */
export interface QueueEntry {
  id: string;
  encounter_id: string;
  queue_type: QueueType;
  ticket_code: string;
  patient_name: string;
  specialty_name: string;
  /** Serviço a realizar; nulo em atendimentos anteriores ao catálogo. */
  service_name: string | null;
  laterality_label: string;
  professional_name: string;
  status: QueueEntryStatus;
  status_label: string;
  encounter_status: EncounterStatus;
  encounter_status_label: string;
  entered_at: string;
  finished_at: string | null;
  last_call_destination: string | null;
  last_called_at: string | null;
  last_call_attempt: number | null;
}

export interface QueueCall {
  id: string;
  queue_entry_id: string;
  ticket_code: string;
  patient_name: string;
  destination_type: string;
  destination_label: string;
  attempt_number: number;
  called_at: string;
}

export type ClinicalQueueView = 'active' | 'inactive';

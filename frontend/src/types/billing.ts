export type BillingStatus = 'PENDENTE' | 'PAGO' | 'LIBERADO';
export type PaymentMethod = 'DINHEIRO' | 'PIX' | 'CARTAO_DEBITO' | 'CARTAO_CREDITO';

/** Paciente do dia com a situação financeira do atendimento (Tela 09). */
export interface BillingEntry {
  encounter_id: string;
  ticket_code: string;
  patient_name: string;
  service_name: string;
  payer_label: string;
  insurer_id: string | null;
  guide_number: string;
  payment_method: PaymentMethod | '';
  status: BillingStatus;
  status_label: string;
  amount: string | null;
}

export interface BillingSummary {
  paid: number;
  pending: number;
  released: number;
  received_amount: string;
}

export interface BillingDay {
  date: string;
  today: BillingSummary;
  previous_day: BillingSummary;
  entries: BillingEntry[];
}

export interface HealthInsurer {
  id: string;
  name: string;
}

export interface PaymentInput {
  insurer: string | null;
  guide_number: string;
  payment_method: PaymentMethod;
  amount: string;
}

export interface AuthorizationInput {
  insurer: string;
  guide_number: string;
  amount: string;
}

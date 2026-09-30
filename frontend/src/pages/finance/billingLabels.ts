import type { BadgeTone } from '../../components/ui/Badge';
import type { SelectOption } from '../../components/ui/SelectField';
import type { BillingStatus } from '../../types/billing';

export const BILLING_STATUS_TONES: Record<BillingStatus, BadgeTone> = {
  PAGO: 'success',
  LIBERADO: 'info',
  PENDENTE: 'danger',
};

export const PAYMENT_METHOD_OPTIONS: SelectOption[] = [
  { value: 'CARTAO_CREDITO', label: 'Cartão de Crédito' },
  { value: 'CARTAO_DEBITO', label: 'Cartão de Débito' },
  { value: 'PIX', label: 'Pix' },
  { value: 'DINHEIRO', label: 'Dinheiro' },
];

/** Valor do seletor de convênio que representa atendimento particular. */
export const PARTICULAR = '';

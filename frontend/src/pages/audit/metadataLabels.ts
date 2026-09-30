import type { AuditMetadataValue } from '../../types/audit';
import { formatCurrency } from '../../utils/currency';

// Nomes legíveis das chaves mais comuns dos metadados gravados pelos serviços.
const KEY_LABELS: Record<string, string> = {
  previous_status: 'Situação anterior',
  new_status: 'Nova situação',
  previous_amount: 'Valor anterior',
  new_amount: 'Novo valor',
  ticket_code: 'Senha',
  destination_label: 'Destino',
  attempt_number: 'Tentativa',
  call_attempts: 'Chamadas realizadas',
  changed_fields: 'Campos alterados',
  station_name: 'Posto',
  username: 'Usuário informado',
  method: 'Método HTTP',
  path: 'Endereço',
  required_permission: 'Permissão exigida',
  queue_type: 'Fila',
  operation: 'Operação',
  template: 'Formulário',
  rows: 'Linhas exportadas',
  search: 'Busca',
};

// Identificadores internos não ajudam na leitura; ficam fora do detalhe.
const HIDDEN_KEYS = new Set([
  'reason',
  'patient_id',
  'encounter_id',
  'appointment_id',
  'station_id',
]);

/** "NAO_COMPARECEU" → "Nao compareceu"; valores monetários em R$. */
function formatValue(key: string, value: AuditMetadataValue): string {
  if (key.endsWith('_amount')) return formatCurrency(value as string);
  if (key.endsWith('_status') && typeof value === 'string') {
    const text = value.replace(/_/g, ' ').toLowerCase();
    return text.charAt(0).toUpperCase() + text.slice(1);
  }
  return String(value);
}

/** Pares (rótulo, valor) exibidos no detalhe do evento. */
export function describeMetadata(metadata: Record<string, AuditMetadataValue>): [string, string][] {
  return Object.entries(metadata)
    .filter(([key, value]) => !HIDDEN_KEYS.has(key) && value !== null && value !== '')
    .map(([key, value]) => [KEY_LABELS[key] ?? key, formatValue(key, value)]);
}

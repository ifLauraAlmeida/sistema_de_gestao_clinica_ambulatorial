import type { ExecutionFormField, ProcedureValue } from '../../types/procedure';

/** Valores do formulário como texto, como os campos HTML os manipulam. */
export type ProcedureDraft = Record<string, string>;

/** Converte os valores gravados em rascunho editável. */
export function toProcedureDraft(
  fields: ExecutionFormField[],
  values: Record<string, ProcedureValue> | null,
): ProcedureDraft {
  return Object.fromEntries(
    fields.map((field) => {
      const value = values?.[field.key];
      return [field.key, value === null || value === undefined ? '' : String(value)];
    }),
  );
}

/**
 * Converte o rascunho no formato da API: números como número, sim/não como
 * booleano e campos vazios como nulo. A validação final é do backend.
 */
export function toProcedurePayload(
  fields: ExecutionFormField[],
  draft: ProcedureDraft,
): Record<string, ProcedureValue> {
  return Object.fromEntries(
    fields.map((field) => [field.key, convert(field, draft[field.key] ?? '')]),
  );
}

function convert(field: ExecutionFormField, raw: string): ProcedureValue {
  const text = raw.trim();
  if (!text) return null;
  if (field.field_type === 'BOOLEAN') return text === 'true';
  if (field.field_type === 'NUMBER') {
    const number = Number(text.replace(',', '.'));
    return Number.isNaN(number) ? text : number;
  }
  return text;
}

/** Rótulo com unidade e obrigatoriedade: "Peso (kg) *". */
export function fieldLabel(field: ExecutionFormField): string {
  const unit = field.unit ? ` (${field.unit})` : '';
  return `${field.label}${unit}${field.is_required ? ' *' : ''}`;
}

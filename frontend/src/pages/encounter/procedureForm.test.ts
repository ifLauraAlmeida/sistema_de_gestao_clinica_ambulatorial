import { describe, expect, it } from 'vitest';
import type { ExecutionFormField } from '../../types/procedure';
import { fieldLabel, toProcedureDraft, toProcedurePayload } from './procedureForm';

const field = (
  key: string,
  field_type: ExecutionFormField['field_type'],
  unit = '',
): ExecutionFormField => ({
  key,
  label: key,
  field_type,
  unit,
  options: [],
  is_required: false,
});

const FIELDS = [
  field('peso', 'NUMBER', 'kg'),
  field('repeticao', 'BOOLEAN'),
  field('obs', 'TEXTAREA'),
];

describe('procedureForm', () => {
  it('converte rascunho em valores tipados para a API', () => {
    expect(toProcedurePayload(FIELDS, { peso: '72,5', repeticao: 'false', obs: '  ' })).toEqual({
      peso: 72.5,
      repeticao: false,
      obs: null,
    });
  });

  it('carrega valores gravados como texto editável', () => {
    expect(toProcedureDraft(FIELDS, { peso: 70, repeticao: true, obs: null })).toEqual({
      peso: '70',
      repeticao: 'true',
      obs: '',
    });
  });

  it('mostra unidade no rótulo', () => {
    expect(fieldLabel(field('Peso', 'NUMBER', 'kg'))).toBe('Peso (kg)');
  });
});

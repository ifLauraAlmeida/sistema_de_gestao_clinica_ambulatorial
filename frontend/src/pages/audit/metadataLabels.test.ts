import { describe, expect, it } from 'vitest';
import { describeMetadata } from './metadataLabels';

describe('describeMetadata', () => {
  it('traduz chaves, formata situação e valor e oculta identificadores', () => {
    expect(
      describeMetadata({
        previous_status: 'PENDENTE',
        new_status: 'PAGO',
        new_amount: '150.00',
        patient_id: 'p1',
        reason: 'x',
      }),
    ).toEqual([
      ['Situação anterior', 'Pendente'],
      ['Nova situação', 'Pago'],
      ['Novo valor', 'R$ 150,00'],
    ]);
  });
});

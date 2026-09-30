import { describe, expect, it } from 'vitest';
import { formatCurrency, parseCurrencyInput } from './currency';
import { compareWithPreviousDay } from './trend';

describe('compareWithPreviousDay', () => {
  it('calcula variação e cor conforme o indicador', () => {
    expect(compareWithPreviousDay(16, 13, true)).toMatchObject({
      label: '+23%',
      direction: 'up',
      isFavorable: true,
    });
    expect(compareWithPreviousDay(7, 5, false)).toMatchObject({
      label: '+40%',
      isFavorable: false,
    });
  });

  it('não divide por zero quando ontem não houve registros', () => {
    expect(compareWithPreviousDay(3, 0, true).label).toBe('sem registros no dia anterior');
    expect(compareWithPreviousDay(0, 0, true).label).toBe('sem variação');
  });
});

describe('moeda', () => {
  it('formata e interpreta valores em real', () => {
    expect(formatCurrency('8460.00')).toBe('R$ 8.460,00');
    expect(parseCurrencyInput('1.420,5')).toBe('1420.50');
    expect(parseCurrencyInput('abc')).toBeNull();
  });
});

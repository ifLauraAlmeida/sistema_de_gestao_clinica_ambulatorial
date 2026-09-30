const currencyFormatter = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });

/** "420.00" → "R$ 420,00"; vazio vira "—". */
export function formatCurrency(amount: string | number | null | undefined): string {
  if (amount === null || amount === undefined || amount === '') return '—';
  return currencyFormatter.format(Number(amount));
}

/** "420,00" → "420.00" (formato da API). Retorna null se não for número. */
export function parseCurrencyInput(text: string): string | null {
  const normalized = text.trim().replace(/\./g, '').replace(',', '.');
  if (!normalized || Number.isNaN(Number(normalized))) return null;
  return Number(normalized).toFixed(2);
}

/** "420.00" → "420,00" para edição. */
export function toCurrencyInput(amount: string | null): string {
  return amount ? Number(amount).toFixed(2).replace('.', ',') : '';
}

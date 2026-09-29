/** Nome do serviço com lateralidade, para tabelas ("Raio-X de joelho — Direita"). */
export function serviceWithLaterality(serviceName: string | null, laterality: string): string {
  if (!serviceName) return '—';
  return laterality ? `${serviceName} — ${laterality}` : serviceName;
}

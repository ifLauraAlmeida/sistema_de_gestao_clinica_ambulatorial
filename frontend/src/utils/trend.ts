import type { KpiTrend } from '../components/ui/KpiCard';

/**
 * Variação percentual em relação ao dia anterior.
 *
 * `higherIsBetter` define a cor: mais pagamentos é bom, mais pendências é ruim.
 *
 * Exemplo:
 *   compareWithPreviousDay(16, 13, true) // { label: '+23%', direction: 'up', isFavorable: true, ... }
 */
export function compareWithPreviousDay(
  current: number,
  previous: number,
  higherIsBetter: boolean,
): KpiTrend {
  const caption = 'em relação a ontem';
  if (previous === 0) {
    return current === 0
      ? { label: 'sem variação', direction: 'flat', isFavorable: true, caption }
      : { label: 'sem registros ontem', direction: 'up', isFavorable: higherIsBetter, caption };
  }
  const percent = Math.round(((current - previous) / previous) * 100);
  if (percent === 0) return { label: '0%', direction: 'flat', isFavorable: true, caption };
  const direction = percent > 0 ? 'up' : 'down';
  return {
    label: `${percent > 0 ? '+' : ''}${percent}%`,
    direction,
    isFavorable: (direction === 'up') === higherIsBetter,
    caption,
  };
}

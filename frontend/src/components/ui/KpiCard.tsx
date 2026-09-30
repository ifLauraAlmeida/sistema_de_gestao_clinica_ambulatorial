import type { ReactElement, ReactNode } from 'react';
import { Minus, TrendingDown, TrendingUp } from 'lucide-react';
import styles from './KpiCard.module.css';

type KpiTone = 'info' | 'success' | 'danger';

/** Variação em relação a um período anterior ("+23% em relação a ontem"). */
export interface KpiTrend {
  label: string;
  direction: 'up' | 'down' | 'flat';
  /** A variação é favorável (verde) ou desfavorável (vermelho)? */
  isFavorable: boolean;
  caption: string;
}

interface KpiCardProps {
  label: string;
  value: string | number;
  caption?: string;
  icon: ReactNode;
  tone?: KpiTone;
  trend?: KpiTrend;
}

const TREND_ICONS = { up: TrendingUp, down: TrendingDown, flat: Minus };

/** Indicador numérico com ícone circular, como nas telas de referência 02, 06 e 09. */
export function KpiCard({
  label,
  value,
  caption,
  icon,
  tone = 'info',
  trend,
}: KpiCardProps): ReactElement {
  const TrendIcon = trend ? TREND_ICONS[trend.direction] : null;

  return (
    <article className={`${styles.kpi} ${styles[tone]}`} aria-label={label}>
      <span className={styles.icon} aria-hidden="true">
        {icon}
      </span>
      <div>
        <p className={styles.label}>{label}</p>
        <p className={styles.value}>{value}</p>
        {trend && TrendIcon && (
          <p
            className={`${styles.trend} ${trend.isFavorable ? styles.favorable : styles.unfavorable}`}
          >
            <TrendIcon size={16} aria-hidden="true" />
            {trend.label}
          </p>
        )}
        {(trend?.caption ?? caption) && (
          <p className={styles.caption}>{trend?.caption ?? caption}</p>
        )}
      </div>
    </article>
  );
}

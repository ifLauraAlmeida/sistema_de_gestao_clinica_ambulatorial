import type { ReactElement, ReactNode } from 'react';
import styles from './KpiCard.module.css';

type KpiTone = 'info' | 'success' | 'danger';

interface KpiCardProps {
  label: string;
  value: string | number;
  caption?: string;
  icon: ReactNode;
  tone?: KpiTone;
}

/** Indicador numérico com ícone circular, como nas telas de referência 02 e 06. */
export function KpiCard({
  label,
  value,
  caption,
  icon,
  tone = 'info',
}: KpiCardProps): ReactElement {
  return (
    <article className={`${styles.kpi} ${styles[tone]}`} aria-label={label}>
      <span className={styles.icon} aria-hidden="true">
        {icon}
      </span>
      <div>
        <p className={styles.label}>{label}</p>
        <p className={styles.value}>{value}</p>
        {caption && <p className={styles.caption}>{caption}</p>}
      </div>
    </article>
  );
}

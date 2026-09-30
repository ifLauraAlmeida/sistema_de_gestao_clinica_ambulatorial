import type { ReactElement, ReactNode } from 'react';
import styles from './Badge.module.css';

export type BadgeTone = 'info' | 'success' | 'warning' | 'danger' | 'neutral';

interface BadgeProps {
  tone?: BadgeTone;
  /** Ponto colorido antes do texto (situações de pagamento, Tela 09). */
  withDot?: boolean;
  children: ReactNode;
}

export function Badge({ tone = 'neutral', withDot = false, children }: BadgeProps): ReactElement {
  return (
    <span className={`${styles.badge} ${styles[tone]}`}>
      {withDot && <span className={styles.dot} aria-hidden="true" />}
      {children}
    </span>
  );
}

import type { ReactElement, ReactNode } from 'react';
import styles from './Badge.module.css';

export type BadgeTone = 'info' | 'success' | 'warning' | 'danger' | 'neutral';

interface BadgeProps {
  tone?: BadgeTone;
  children: ReactNode;
}

export function Badge({ tone = 'neutral', children }: BadgeProps): ReactElement {
  return <span className={`${styles.badge} ${styles[tone]}`}>{children}</span>;
}

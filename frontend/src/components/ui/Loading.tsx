import type { ReactElement } from 'react';
import styles from './Loading.module.css';

interface LoadingProps {
  label?: string;
  fullScreen?: boolean;
}

export function Loading({ label = 'Carregando…', fullScreen = false }: LoadingProps): ReactElement {
  return (
    <div className={`${styles.loading} ${fullScreen ? styles.fullScreen : ''}`} role="status">
      <span className={styles.spinner} aria-hidden="true" />
      <span>{label}</span>
    </div>
  );
}

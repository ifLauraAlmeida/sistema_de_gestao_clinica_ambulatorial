import type { ReactElement, ReactNode } from 'react';
import styles from './Card.module.css';

interface CardProps {
  title?: string;
  icon?: ReactNode;
  actions?: ReactNode;
  children: ReactNode;
  className?: string;
}

export function Card({ title, icon, actions, children, className }: CardProps): ReactElement {
  return (
    <section className={`${styles.card} ${className ?? ''}`} aria-label={title}>
      {(title || actions) && (
        <header className={styles.header}>
          <h2 className={styles.title}>
            {icon && <span className={styles.icon}>{icon}</span>}
            {title}
          </h2>
          {actions}
        </header>
      )}
      {children}
    </section>
  );
}

import type { ReactElement, ReactNode } from 'react';
import styles from './Card.module.css';

interface CardProps {
  title?: string;
  subtitle?: string;
  icon?: ReactNode;
  actions?: ReactNode;
  children: ReactNode;
  className?: string;
}

export function Card({
  title,
  subtitle,
  icon,
  actions,
  children,
  className,
}: CardProps): ReactElement {
  return (
    <section className={`${styles.card} ${className ?? ''}`} aria-label={title}>
      {(title || actions) && (
        <header className={styles.header}>
          <div>
            <h2 className={styles.title}>
              {icon && <span className={styles.icon}>{icon}</span>}
              {title}
            </h2>
            {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
          </div>
          {actions}
        </header>
      )}
      {children}
    </section>
  );
}

import { useId, type InputHTMLAttributes, type ReactElement } from 'react';
import styles from './CheckboxField.module.css';

interface CheckboxFieldProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'id' | 'type'> {
  label: string;
  hint?: string;
}

export function CheckboxField({ label, hint, ...rest }: CheckboxFieldProps): ReactElement {
  const inputId = useId();
  return (
    <label htmlFor={inputId} className={styles.field}>
      <input id={inputId} type="checkbox" className={styles.checkbox} {...rest} />
      <span>
        {label}
        {hint && <span className={styles.hint}> — {hint}</span>}
      </span>
    </label>
  );
}

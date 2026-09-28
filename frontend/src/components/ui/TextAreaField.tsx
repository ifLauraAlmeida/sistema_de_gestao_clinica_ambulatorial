import { useId, type ReactElement, type TextareaHTMLAttributes } from 'react';
import styles from './TextAreaField.module.css';

interface TextAreaFieldProps extends Omit<TextareaHTMLAttributes<HTMLTextAreaElement>, 'id'> {
  label: string;
  error?: string;
}

export function TextAreaField({ label, error, ...rest }: TextAreaFieldProps): ReactElement {
  const fieldId = useId();
  const errorId = `${fieldId}-error`;

  return (
    <div className={styles.field}>
      <label htmlFor={fieldId} className={styles.label}>
        {label}
      </label>
      <textarea
        id={fieldId}
        className={`${styles.textarea} ${error ? styles.invalid : ''}`}
        aria-invalid={Boolean(error)}
        aria-describedby={error ? errorId : undefined}
        rows={3}
        {...rest}
      />
      {error && (
        <p id={errorId} className={styles.error}>
          {error}
        </p>
      )}
    </div>
  );
}

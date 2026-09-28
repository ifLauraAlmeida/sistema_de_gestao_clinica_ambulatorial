import { useId, type ReactElement, type SelectHTMLAttributes } from 'react';
import { ChevronDown } from 'lucide-react';
import styles from './SelectField.module.css';

export interface SelectOption {
  value: string;
  label: string;
}

interface SelectFieldProps extends Omit<SelectHTMLAttributes<HTMLSelectElement>, 'id'> {
  label: string;
  options: SelectOption[];
  placeholder?: string;
  error?: string;
}

/** Lista de seleção com rótulo associado e mensagem de erro acessível. */
export function SelectField({
  label,
  options,
  placeholder,
  error,
  ...rest
}: SelectFieldProps): ReactElement {
  const selectId = useId();
  const errorId = `${selectId}-error`;

  return (
    <div className={styles.field}>
      <label htmlFor={selectId} className={styles.label}>
        {label}
      </label>
      <div className={`${styles.control} ${error ? styles.invalid : ''}`}>
        <select
          id={selectId}
          className={styles.select}
          aria-invalid={Boolean(error)}
          aria-describedby={error ? errorId : undefined}
          {...rest}
        >
          {placeholder !== undefined && <option value="">{placeholder}</option>}
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <ChevronDown size={18} className={styles.chevron} aria-hidden="true" />
      </div>
      {error && (
        <p id={errorId} className={styles.error}>
          {error}
        </p>
      )}
    </div>
  );
}

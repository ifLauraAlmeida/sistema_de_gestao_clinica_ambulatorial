import {
  useId,
  useState,
  type InputHTMLAttributes,
  type ReactElement,
  type ReactNode,
} from 'react';
import { Eye, EyeOff } from 'lucide-react';
import styles from './TextField.module.css';

interface TextFieldProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'id'> {
  label: string;
  icon?: ReactNode;
  error?: string;
}

/** Campo de texto com rótulo associado, ícone e alternância de visibilidade para senhas. */
export function TextField({
  label,
  icon,
  error,
  type = 'text',
  ...rest
}: TextFieldProps): ReactElement {
  const inputId = useId();
  const errorId = `${inputId}-error`;
  const [isPasswordVisible, setPasswordVisible] = useState(false);
  const isPassword = type === 'password';
  const effectiveType = isPassword && isPasswordVisible ? 'text' : type;

  return (
    <div className={styles.field}>
      <label htmlFor={inputId} className={styles.label}>
        {label}
      </label>
      <div className={`${styles.control} ${error ? styles.invalid : ''}`}>
        {icon && <span className={styles.icon}>{icon}</span>}
        <input
          id={inputId}
          type={effectiveType}
          className={styles.input}
          aria-invalid={Boolean(error)}
          aria-describedby={error ? errorId : undefined}
          {...rest}
        />
        {isPassword && (
          <button
            type="button"
            className={styles.toggle}
            onClick={() => setPasswordVisible((visible) => !visible)}
            aria-label={isPasswordVisible ? 'Ocultar senha' : 'Mostrar senha'}
            aria-pressed={isPasswordVisible}
          >
            {isPasswordVisible ? <EyeOff size={18} /> : <Eye size={18} />}
          </button>
        )}
      </div>
      {error && (
        <p id={errorId} className={styles.error}>
          {error}
        </p>
      )}
    </div>
  );
}

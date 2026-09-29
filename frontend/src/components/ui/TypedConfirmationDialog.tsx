import { useEffect, useId, useState, type ReactElement, type ReactNode } from 'react';
import { AlertTriangle } from 'lucide-react';
import { isConfirmationWordTyped } from '../../utils/confirmationWord';
import { Button } from './Button';
import { TextField } from './TextField';
import styles from './TypedConfirmationDialog.module.css';

interface TypedConfirmationDialogProps {
  title: string;
  children: ReactNode;
  confirmationWord: string;
  confirmLabel: string;
  isBusy: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

/**
 * Confirmação para ações irreversíveis: o usuário precisa DIGITAR a palavra
 * sorteada (colar é bloqueado) antes de liberar o botão.
 */
export function TypedConfirmationDialog({
  title,
  children,
  confirmationWord,
  confirmLabel,
  isBusy,
  onConfirm,
  onCancel,
}: TypedConfirmationDialogProps): ReactElement {
  const titleId = useId();
  const [typed, setTyped] = useState('');
  const isConfirmed = isConfirmationWordTyped(typed, confirmationWord);

  useEffect(() => {
    const closeOnEscape = (event: KeyboardEvent): void => {
      if (event.key === 'Escape' && !isBusy) onCancel();
    };
    window.addEventListener('keydown', closeOnEscape);
    return () => window.removeEventListener('keydown', closeOnEscape);
  }, [isBusy, onCancel]);

  return (
    <div className={styles.backdrop}>
      <div className={styles.dialog} role="alertdialog" aria-modal="true" aria-labelledby={titleId}>
        <header className={styles.header}>
          <span className={styles.icon} aria-hidden="true">
            <AlertTriangle size={24} />
          </span>
          <h2 id={titleId}>{title}</h2>
        </header>
        <div className={styles.body}>{children}</div>
        <p className={styles.instruction}>
          Digite <strong className={styles.word}>{confirmationWord}</strong> para confirmar.
        </p>
        <TextField
          label={`Digite ${confirmationWord} para confirmar`}
          value={typed}
          autoFocus
          autoComplete="off"
          spellCheck={false}
          onChange={(event) => setTyped(event.target.value)}
          onPaste={(event) => event.preventDefault()}
          onDrop={(event) => event.preventDefault()}
        />
        <footer className={styles.footer}>
          <Button variant="secondary" onClick={onCancel} disabled={isBusy}>
            Cancelar
          </Button>
          <Button variant="danger" disabled={!isConfirmed} isLoading={isBusy} onClick={onConfirm}>
            {confirmLabel}
          </Button>
        </footer>
      </div>
    </div>
  );
}

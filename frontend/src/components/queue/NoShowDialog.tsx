import type { ReactElement } from 'react';
import { TypedConfirmationDialog } from '../ui/TypedConfirmationDialog';
import type { QueueEntry } from '../../types/queue';

interface NoShowDialogProps {
  entry: QueueEntry;
  confirmationWord: string;
  isBusy: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

/** Confirmação reforçada do não comparecimento (ação irreversível). */
export function NoShowDialog({
  entry,
  confirmationWord,
  isBusy,
  onConfirm,
  onCancel,
}: NoShowDialogProps): ReactElement {
  const attempts = entry.last_call_attempt ?? 0;

  return (
    <TypedConfirmationDialog
      title="Registrar não comparecimento?"
      confirmationWord={confirmationWord}
      confirmLabel="Registrar falta"
      isBusy={isBusy}
      onConfirm={onConfirm}
      onCancel={onCancel}
    >
      <p>
        Você realmente deseja registrar a falta de <strong>{entry.patient_name}</strong> (senha{' '}
        <strong>{entry.ticket_code}</strong>)? A senha foi chamada {attempts}{' '}
        {attempts === 1 ? 'vez' : 'vezes'}.
      </p>
      <ul>
        <li>
          A ação é <strong>irrevogável</strong>: a senha sai da fila e não poderá ser chamada
          novamente.
        </li>
        <li>Você não terá mais acesso a esta ficha por este atendimento.</li>
        <li>
          Se o paciente pode não ter ouvido a chamada, feche esta janela e use{' '}
          <strong>Rechamar</strong>.
        </li>
      </ul>
    </TypedConfirmationDialog>
  );
}

import { useState, type ReactElement } from 'react';
import { NoShowDialog } from '../components/queue/NoShowDialog';
import type { QueueEntry } from '../types/queue';
import { pickConfirmationWord } from '../utils/confirmationWord';

interface NoShowConfirmation {
  requestNoShow: (entry: QueueEntry) => void;
  dialog: ReactElement | null;
}

/**
 * Controla a janela de confirmação do não comparecimento. Cada abertura sorteia
 * uma nova palavra a ser digitada.
 *
 * `runOperation` executa a chamada à API (com feedback e recarga da fila).
 */
export function useNoShowConfirmation(
  markNoShow: (entryId: string) => Promise<void>,
  runOperation: (key: string, operation: () => Promise<string>) => Promise<void>,
  busyKey: string | null,
): NoShowConfirmation {
  const [pending, setPending] = useState<{ entry: QueueEntry; word: string } | null>(null);

  const requestNoShow = (entry: QueueEntry): void =>
    setPending({ entry, word: pickConfirmationWord() });

  const confirm = async (entry: QueueEntry): Promise<void> => {
    await runOperation(`no-show-${entry.id}`, async () => {
      await markNoShow(entry.id);
      return `Não comparecimento registrado para a senha ${entry.ticket_code}.`;
    });
    setPending(null);
  };

  const dialog = pending && (
    <NoShowDialog
      entry={pending.entry}
      confirmationWord={pending.word}
      isBusy={busyKey === `no-show-${pending.entry.id}`}
      onConfirm={() => void confirm(pending.entry)}
      onCancel={() => setPending(null)}
    />
  );

  return { requestNoShow, dialog };
}

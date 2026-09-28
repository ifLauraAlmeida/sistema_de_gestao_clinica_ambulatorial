import { useCallback, useState } from 'react';
import { describeError } from '../utils/errorMessages';

interface QueueOperation {
  busyKey: string | null;
  errorMessage: string | null;
  successMessage: string | null;
  run: (key: string, operation: () => Promise<string>) => Promise<void>;
}

/**
 * Executa uma ação de fila (chamar, encaminhar, finalizar) com estado de
 * carregamento, mensagem de retorno e recarga das listas.
 *
 * `operation` retorna a mensagem de sucesso exibida ao usuário.
 */
export function useQueueOperation(onCompleted: () => Promise<void>): QueueOperation {
  const [busyKey, setBusyKey] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const run = useCallback(
    async (key: string, operation: () => Promise<string>): Promise<void> => {
      setBusyKey(key);
      setErrorMessage(null);
      setSuccessMessage(null);
      try {
        setSuccessMessage(await operation());
      } catch (error) {
        setErrorMessage(describeError(error, 'Não foi possível concluir a operação.'));
      } finally {
        setBusyKey(null);
        await onCompleted();
      }
    },
    [onCompleted],
  );

  return { busyKey, errorMessage, successMessage, run };
}

import type { ReactElement } from 'react';
import { ArrowRightCircle, CheckCircle2, Megaphone, RotateCcw } from 'lucide-react';
import { Button } from '../ui/Button';
import type { QueueEntry } from '../../types/queue';
import styles from './Queue.module.css';

interface QueueRowActionsProps {
  entry: QueueEntry;
  busyKey: string | null;
  canCall: boolean;
  hasDestination: boolean;
  onCall: (entry: QueueEntry) => void;
  onForward?: (entry: QueueEntry) => void;
  onComplete?: (entry: QueueEntry) => void;
}

/**
 * Ações de uma senha na fila. Exibir ou ocultar botões é apenas conveniência:
 * o backend valida perfil, dono da fila e posto em cada chamada.
 */
export function QueueRowActions({
  entry,
  busyKey,
  canCall,
  hasDestination,
  onCall,
  onForward,
  onComplete,
}: QueueRowActionsProps): ReactElement {
  const isRecall = entry.status === 'CALLED';

  return (
    <div className={styles.rowActions}>
      {canCall && (
        <Button
          variant="secondary"
          icon={isRecall ? <RotateCcw size={16} /> : <Megaphone size={16} />}
          disabled={!hasDestination}
          title={hasDestination ? undefined : 'Selecione um posto de trabalho para chamar'}
          isLoading={busyKey === `call-${entry.id}`}
          onClick={() => onCall(entry)}
        >
          {isRecall ? 'Rechamar' : 'Chamar'}
        </Button>
      )}
      {onForward && (
        <Button
          variant="ghost"
          icon={<ArrowRightCircle size={16} />}
          isLoading={busyKey === `forward-${entry.id}`}
          onClick={() => onForward(entry)}
        >
          Encaminhar
        </Button>
      )}
      {onComplete && entry.encounter_status === 'CHAMADO' && (
        <Button
          variant="primary"
          icon={<CheckCircle2 size={16} />}
          isLoading={busyKey === `complete-${entry.id}`}
          onClick={() => onComplete(entry)}
        >
          Finalizar atendimento
        </Button>
      )}
    </div>
  );
}

import type { ReactElement } from 'react';
import {
  ArrowRightCircle,
  CheckCircle2,
  Megaphone,
  PlayCircle,
  RotateCcw,
  UserX,
} from 'lucide-react';
import { Button } from '../ui/Button';
import { EncounterRecordLink } from './EncounterRecordLink';
import type { QueueEntry } from '../../types/queue';
import { canCompleteEncounter, canMarkNoShow, canStartEncounter } from '../../utils/queueMetrics';
import styles from './Queue.module.css';

interface QueueRowActionsProps {
  entry: QueueEntry;
  busyKey: string | null;
  canCall: boolean;
  hasDestination: boolean;
  onCall: (entry: QueueEntry) => void;
  onForward?: (entry: QueueEntry) => void;
  onStart?: (entry: QueueEntry) => void;
  /** Abre a confirmação de não comparecimento (somente senhas já chamadas). */
  onNoShow?: (entry: QueueEntry) => void;
  onComplete?: (entry: QueueEntry) => void;
  /** Exibe o acesso à tela de atendimento/prontuário. */
  showRecordLink?: boolean;
}

/**
 * Ações de uma senha na fila. Exibir ou ocultar botões é apenas conveniência:
 * o backend valida perfil, dono da fila, posto e status em cada operação.
 */
export function QueueRowActions({
  entry,
  busyKey,
  canCall,
  hasDestination,
  onCall,
  onForward,
  onStart,
  onNoShow,
  onComplete,
  showRecordLink = false,
}: QueueRowActionsProps): ReactElement {
  const isRecall = entry.status === 'CALLED';

  return (
    <div className={styles.rowActions}>
      {canCall && entry.encounter_status !== 'EM_ATENDIMENTO' && (
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
      {onStart && canStartEncounter(entry) && (
        <Button
          variant="secondary"
          icon={<PlayCircle size={16} />}
          isLoading={busyKey === `start-${entry.id}`}
          onClick={() => onStart(entry)}
        >
          Iniciar atendimento
        </Button>
      )}
      {onNoShow && canMarkNoShow(entry) && (
        <Button
          variant="danger"
          icon={<UserX size={16} />}
          disabled={busyKey !== null}
          onClick={() => onNoShow(entry)}
        >
          Não compareceu
        </Button>
      )}
      {showRecordLink && <EncounterRecordLink encounterId={entry.encounter_id} />}
      {onComplete && canCompleteEncounter(entry) && (
        <Button
          variant="primary"
          icon={<CheckCircle2 size={16} />}
          isLoading={busyKey === `complete-${entry.id}`}
          onClick={() => onComplete(entry)}
        >
          Finalizar
        </Button>
      )}
    </div>
  );
}

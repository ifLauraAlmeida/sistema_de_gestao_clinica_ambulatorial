import { useState, type ReactElement } from 'react';
import { CheckCircle2, PlayCircle } from 'lucide-react';
import { Alert } from '../../components/ui/Alert';
import { Button } from '../../components/ui/Button';
import type { EncounterSummary } from '../../types/medicalRecord';
import styles from './EncounterPage.module.css';

interface EncounterActionsProps {
  encounter: EncounterSummary;
  canStart: boolean;
  canComplete: boolean;
  busyAction: 'start' | 'complete' | null;
  onStart: () => void;
  onComplete: () => void;
}

/** Iniciar e finalizar o atendimento; finalizar pede confirmação explícita. */
export function EncounterActions({
  encounter,
  canStart,
  canComplete,
  busyAction,
  onStart,
  onComplete,
}: EncounterActionsProps): ReactElement | null {
  const [isConfirming, setConfirming] = useState(false);
  const showStart = canStart && encounter.status === 'CHAMADO';
  const showComplete =
    canComplete && (encounter.status === 'CHAMADO' || encounter.status === 'EM_ATENDIMENTO');

  if (!showStart && !showComplete) return null;

  if (isConfirming) {
    return (
      <div className={styles.confirmBox} role="alertdialog" aria-label="Confirmar finalização">
        <Alert tone="info">
          Ao finalizar, o atendimento vai para a fila inativa e o prontuário deixa de ficar
          acessível por este atendimento. Os registros permanecem salvos.
        </Alert>
        <div className={styles.actionsRow}>
          <Button variant="secondary" onClick={() => setConfirming(false)}>
            Voltar
          </Button>
          <Button
            icon={<CheckCircle2 size={18} />}
            isLoading={busyAction === 'complete'}
            onClick={onComplete}
          >
            Confirmar finalização
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.actionsRow}>
      {showStart && (
        <Button
          variant="secondary"
          icon={<PlayCircle size={18} />}
          isLoading={busyAction === 'start'}
          onClick={onStart}
        >
          Iniciar atendimento
        </Button>
      )}
      {showComplete && (
        <Button icon={<CheckCircle2 size={18} />} onClick={() => setConfirming(true)}>
          Finalizar atendimento
        </Button>
      )}
    </div>
  );
}

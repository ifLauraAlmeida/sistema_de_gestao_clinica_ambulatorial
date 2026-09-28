import type { ReactElement } from 'react';
import { Volume2 } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { EmptyState } from '../../components/ui/EmptyState';
import type { QueueEntry } from '../../types/queue';
import { waitingMinutes } from '../../utils/queueMetrics';
import styles from './Dashboard.module.css';

interface CallPanelProps {
  nextEntry: QueueEntry | undefined;
  destinationLabel: string | undefined;
  now: Date;
  isCalling: boolean;
  onCall: (entry: QueueEntry) => void;
}

/** Painel "Chamada de paciente" (Tela 06): próxima senha e destino atual. */
export function CallPanel({
  nextEntry,
  destinationLabel,
  now,
  isCalling,
  onCall,
}: CallPanelProps): ReactElement {
  return (
    <Card title="Chamada de paciente" icon={<Volume2 size={20} />}>
      {nextEntry ? (
        <div className={styles.nextTicket}>
          <span className={styles.nextLabel}>Próxima senha</span>
          <span className={styles.nextCode}>{nextEntry.ticket_code}</span>
          <span className={styles.nextPatient}>{nextEntry.patient_name}</span>
          <span className={styles.nextMeta}>
            {nextEntry.specialty_name} • {waitingMinutes(nextEntry, now)} min de espera
          </span>
        </div>
      ) : (
        <EmptyState title="Nenhuma senha aguardando" />
      )}
      <p className={styles.destination}>
        Destino da chamada: <strong>{destinationLabel ?? 'nenhum posto selecionado'}</strong>
      </p>
      <Button
        size="lg"
        fullWidth
        icon={<Volume2 size={20} />}
        disabled={!nextEntry || !destinationLabel}
        isLoading={isCalling}
        onClick={() => nextEntry && onCall(nextEntry)}
      >
        Chamar próxima senha
      </Button>
    </Card>
  );
}

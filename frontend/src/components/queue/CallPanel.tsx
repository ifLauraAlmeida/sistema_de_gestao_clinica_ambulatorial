import type { ReactElement } from 'react';
import { RotateCcw, Volume2 } from 'lucide-react';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import { EmptyState } from '../ui/EmptyState';
import { SelectField } from '../ui/SelectField';
import type { QueueEntry } from '../../types/queue';
import { waitingMinutes } from '../../utils/queueMetrics';
import styles from './Queue.module.css';

interface CallPanelProps {
  entries: QueueEntry[];
  selectedEntry: QueueEntry | undefined;
  destinationLabel: string | undefined;
  now: Date;
  isCalling: boolean;
  onSelect: (entryId: string) => void;
  onCall: (entry: QueueEntry) => void;
}

/**
 * Painel "Chamada de paciente" (Tela 06). Sugere a próxima senha, mas permite
 * escolher qualquer senha da fila (ex.: prioridade, retorno ou exame).
 */
export function CallPanel({
  entries,
  selectedEntry,
  destinationLabel,
  now,
  isCalling,
  onSelect,
  onCall,
}: CallPanelProps): ReactElement {
  const isRecall = selectedEntry?.status === 'CALLED';

  return (
    <Card title="Chamada de paciente" icon={<Volume2 size={20} />}>
      {entries.length > 0 && (
        <SelectField
          label="Senha a chamar"
          value={selectedEntry?.id ?? ''}
          onChange={(event) => onSelect(event.target.value)}
          options={entries.map((entry) => ({
            value: entry.id,
            label: `${entry.ticket_code} — ${entry.patient_name} (${entry.status_label})`,
          }))}
        />
      )}
      {selectedEntry ? (
        <div className={styles.nextTicket} aria-live="polite">
          <span className={styles.nextLabel}>Senha selecionada</span>
          <span className={styles.nextCode}>{selectedEntry.ticket_code}</span>
          <span className={styles.nextPatient}>{selectedEntry.patient_name}</span>
          <span className={styles.nextMeta}>
            {selectedEntry.service_name ?? selectedEntry.specialty_name} •{' '}
            {waitingMinutes(selectedEntry, now)} min de espera
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
        icon={isRecall ? <RotateCcw size={20} /> : <Volume2 size={20} />}
        disabled={!selectedEntry || !destinationLabel}
        isLoading={isCalling}
        onClick={() => selectedEntry && onCall(selectedEntry)}
      >
        {isRecall ? `Rechamar ${selectedEntry.ticket_code}` : 'Chamar senha selecionada'}
      </Button>
    </Card>
  );
}

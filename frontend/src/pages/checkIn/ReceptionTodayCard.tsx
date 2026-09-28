import type { ReactElement } from 'react';
import { Link } from 'react-router-dom';
import { ListOrdered } from 'lucide-react';
import { QueueTable } from '../../components/queue/QueueTable';
import { Card } from '../../components/ui/Card';
import type { QueueEntry } from '../../types/queue';
import { summarizeQueue } from '../../utils/queueMetrics';
import styles from './CheckInPage.module.css';

const PREVIEW_SIZE = 5;

interface ReceptionTodayCardProps {
  entries: QueueEntry[];
  now: Date;
}

/** Resumo da fila da recepção exibido ao lado do check-in (Tela 05). */
export function ReceptionTodayCard({ entries, now }: ReceptionTodayCardProps): ReactElement {
  const summary = summarizeQueue(entries, now);

  return (
    <Card
      title="Fila de hoje"
      icon={<ListOrdered size={20} />}
      actions={<Link to="/fila-recepcao">Ver fila completa</Link>}
    >
      <div className={styles.counters}>
        <span>
          <strong>{summary.waiting}</strong> aguardando
        </span>
        <span>
          <strong>{summary.called}</strong> chamados
        </span>
      </div>
      <QueueTable
        caption="Próximos da fila"
        entries={entries.slice(0, PREVIEW_SIZE)}
        now={now}
        emptyTitle="Ninguém na fila da recepção"
      />
    </Card>
  );
}

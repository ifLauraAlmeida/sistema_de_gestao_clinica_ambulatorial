import type { ReactElement } from 'react';
import { AlertTriangle, Clock, Megaphone, Users } from 'lucide-react';
import { KpiCard } from '../../components/ui/KpiCard';
import { LONG_WAIT_MINUTES, type QueueSummary } from '../../utils/queueMetrics';
import styles from './Dashboard.module.css';

interface QueueKpisProps {
  summary: QueueSummary;
  waitingLabel: string;
}

export function QueueKpis({ summary, waitingLabel }: QueueKpisProps): ReactElement {
  return (
    <div className={styles.kpis}>
      <KpiCard
        icon={<Users size={26} />}
        label={waitingLabel}
        value={summary.waiting}
        caption="aguardando"
      />
      <KpiCard
        icon={<Megaphone size={26} />}
        label="Chamados"
        value={summary.called}
        caption="aguardando comparecimento"
        tone="success"
      />
      <KpiCard
        icon={<Clock size={26} />}
        label="Tempo médio de espera"
        value={`${summary.averageWaitMinutes} min`}
        caption="desde a entrada na fila"
      />
      <KpiCard
        icon={<AlertTriangle size={26} />}
        label={`Aguardando há mais de ${LONG_WAIT_MINUTES} min`}
        value={summary.longWaitCount}
        caption="pacientes"
        tone={summary.longWaitCount > 0 ? 'danger' : 'info'}
      />
    </div>
  );
}

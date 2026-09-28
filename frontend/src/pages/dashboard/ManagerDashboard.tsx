import type { ReactElement } from 'react';
import { CheckCircle2, ListOrdered, Stethoscope, Users } from 'lucide-react';
import { Card } from '../../components/ui/Card';
import { KpiCard } from '../../components/ui/KpiCard';
import { PageHeader } from '../../components/ui/PageHeader';
import { useApiResource } from '../../hooks/useApiResource';
import { useCurrentUser } from '../../hooks/useAuth';
import { useNow } from '../../hooks/useNow';
import { listClinicalQueue, listReceptionQueue } from '../../services/queues';
import type { QueueEntry } from '../../types/queue';
import { summarizeQueue } from '../../utils/queueMetrics';
import { firstNameOf } from '../../utils/userAccess';
import { QUEUE_REFRESH_INTERVAL_MS } from '../../components/queue/queueRefresh';
import { QueueTable } from '../../components/queue/QueueTable';
import { TodayBadge } from '../../components/queue/TodayBadge';
import styles from '../../layouts/PageGrid.module.css';

const loadActiveClinical = (): Promise<QueueEntry[]> => listClinicalQueue('active');
const loadInactiveClinical = (): Promise<QueueEntry[]> => listClinicalQueue('inactive');

/** Visão geral do gestor: todas as filas do dia, somente leitura. */
export function ManagerDashboard(): ReactElement {
  const user = useCurrentUser();
  const now = useNow();
  const refresh = { refreshIntervalMs: QUEUE_REFRESH_INTERVAL_MS };
  const reception = useApiResource(listReceptionQueue, refresh).data ?? [];
  const clinical = useApiResource(loadActiveClinical, refresh).data ?? [];
  const attended = useApiResource(loadInactiveClinical, refresh).data ?? [];
  const clinicalSummary = summarizeQueue(clinical, now);

  return (
    <>
      <PageHeader
        title={`Olá, ${firstNameOf(user)}!`}
        subtitle="Visão geral do atendimento da clínica hoje."
        actions={<TodayBadge now={now} />}
      />
      <div className={styles.kpis}>
        <KpiCard icon={<Users size={26} />} label="Na recepção" value={reception.length} />
        <KpiCard
          icon={<Stethoscope size={26} />}
          label="Aguardando profissional"
          value={clinicalSummary.waiting}
          caption={`tempo médio ${clinicalSummary.averageWaitMinutes} min`}
        />
        <KpiCard
          icon={<ListOrdered size={26} />}
          label="Em chamada"
          value={clinicalSummary.called}
          tone="success"
        />
        <KpiCard
          icon={<CheckCircle2 size={26} />}
          label="Atendidos hoje"
          value={attended.length}
          tone="success"
        />
      </div>
      <Card title="Fila da recepção" icon={<ListOrdered size={20} />}>
        <QueueTable
          caption="Fila da recepção"
          entries={reception}
          now={now}
          showProfessional
          emptyTitle="Nenhum paciente na recepção"
        />
      </Card>
      <Card title="Filas clínicas" icon={<Stethoscope size={20} />}>
        <QueueTable
          caption="Filas clínicas"
          entries={clinical}
          now={now}
          showProfessional
          emptyTitle="Nenhum paciente aguardando profissionais"
        />
      </Card>
    </>
  );
}

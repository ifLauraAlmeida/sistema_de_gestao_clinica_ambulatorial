import type { ReactElement } from 'react';
import { Link } from 'react-router-dom';
import { CheckCircle2, Stethoscope } from 'lucide-react';
import { QueueKpis } from '../../components/queue/QueueKpis';
import { QueueTable } from '../../components/queue/QueueTable';
import { TodayBadge } from '../../components/queue/TodayBadge';
import { QUEUE_REFRESH_INTERVAL_MS } from '../../components/queue/queueRefresh';
import { Card } from '../../components/ui/Card';
import { KpiCard } from '../../components/ui/KpiCard';
import { PageHeader } from '../../components/ui/PageHeader';
import { useApiResource } from '../../hooks/useApiResource';
import { useCurrentUser } from '../../hooks/useAuth';
import { useNow } from '../../hooks/useNow';
import { listClinicalQueue } from '../../services/queues';
import type { QueueEntry } from '../../types/queue';
import { summarizeQueue } from '../../utils/queueMetrics';
import { firstNameOf } from '../../utils/userAccess';
import grid from '../../layouts/PageGrid.module.css';

const REFRESH = { refreshIntervalMs: QUEUE_REFRESH_INTERVAL_MS };
const PREVIEW_SIZE = 5;
const loadActiveQueue = (): Promise<QueueEntry[]> => listClinicalQueue('active');
const loadInactiveQueue = (): Promise<QueueEntry[]> => listClinicalQueue('inactive');

/** Resumo do dia do médico; as chamadas acontecem em "Minha fila clínica". */
export function DoctorDashboard(): ReactElement {
  const user = useCurrentUser();
  const now = useNow();
  const active = useApiResource(loadActiveQueue, REFRESH).data ?? [];
  const attended = useApiResource(loadInactiveQueue, REFRESH).data ?? [];

  return (
    <>
      <PageHeader
        title={`Olá, ${firstNameOf(user)}!`}
        subtitle="Sua fila de atendimento de hoje."
        actions={<TodayBadge now={now} />}
      />
      <QueueKpis summary={summarizeQueue(active, now)} waitingLabel="Na minha fila" />
      <div className={grid.columns}>
        <Card
          title="Próximos da minha fila"
          icon={<Stethoscope size={20} />}
          actions={<Link to="/fila-clinica">Ir para minha fila</Link>}
        >
          <QueueTable
            caption="Próximos da minha fila"
            entries={active.slice(0, PREVIEW_SIZE)}
            now={now}
            emptyTitle="Nenhum paciente na sua fila"
          />
        </Card>
        <KpiCard
          icon={<CheckCircle2 size={26} />}
          label="Atendidos hoje"
          value={attended.length}
          caption="fila inativa"
          tone="success"
        />
      </div>
    </>
  );
}

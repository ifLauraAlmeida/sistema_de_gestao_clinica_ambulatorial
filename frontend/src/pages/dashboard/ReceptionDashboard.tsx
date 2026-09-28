import { useCallback, type ReactElement } from 'react';
import { ListOrdered } from 'lucide-react';
import { Alert } from '../../components/ui/Alert';
import { Card } from '../../components/ui/Card';
import { Loading } from '../../components/ui/Loading';
import { PageHeader } from '../../components/ui/PageHeader';
import { useApiResource } from '../../hooks/useApiResource';
import { useCurrentUser } from '../../hooks/useAuth';
import { useNow } from '../../hooks/useNow';
import { useQueueOperation } from '../../hooks/useQueueOperation';
import {
  callReceptionTicket,
  forwardToClinicalQueue,
  listRecentReceptionCalls,
  listReceptionQueue,
} from '../../services/queues';
import type { QueueEntry } from '../../types/queue';
import { nextWaitingEntry, summarizeQueue } from '../../utils/queueMetrics';
import { firstNameOf, hasAnyPermission } from '../../utils/userAccess';
import { CallPanel } from './CallPanel';
import { QUEUE_REFRESH_INTERVAL_MS } from './queueRefresh';
import { QueueKpis } from './QueueKpis';
import { QueueRowActions } from './QueueRowActions';
import { QueueTable } from './QueueTable';
import { RecentCallsCard } from './RecentCallsCard';
import { TodayBadge } from './TodayBadge';
import styles from './Dashboard.module.css';

/** Visão operacional da recepção: somente a fila da recepção (Telas 02 e 06). */
export function ReceptionDashboard(): ReactElement {
  const user = useCurrentUser();
  const now = useNow();
  const refresh = { refreshIntervalMs: QUEUE_REFRESH_INTERVAL_MS };
  const queue = useApiResource(listReceptionQueue, refresh);
  const calls = useApiResource(listRecentReceptionCalls, refresh);
  const { reload: reloadQueue } = queue;
  const { reload: reloadCalls } = calls;
  const reloadAll = useCallback(async () => {
    await Promise.all([reloadQueue(), reloadCalls()]);
  }, [reloadQueue, reloadCalls]);
  const operation = useQueueOperation(reloadAll);

  const entries = queue.data ?? [];
  const destination = user.active_work_session?.station.name;
  const canCall = hasAnyPermission(user, ['reception_queue.call']);
  const canForward = hasAnyPermission(user, ['reception_queue.forward']);

  const callTicket = (entry: QueueEntry): void =>
    void operation.run(`call-${entry.id}`, async () => {
      const call = await callReceptionTicket(entry.id);
      return `Senha ${call.ticket_code} chamada para ${call.destination_label}.`;
    });

  const forwardTicket = (entry: QueueEntry): void =>
    void operation.run(`forward-${entry.id}`, async () => {
      await forwardToClinicalQueue(entry.id);
      return `Senha ${entry.ticket_code} encaminhada para a fila de ${entry.professional_name}.`;
    });

  return (
    <>
      <PageHeader
        title={`Olá, ${firstNameOf(user)}!`}
        subtitle="Acompanhe a fila da recepção e realize as chamadas."
        actions={<TodayBadge now={now} />}
      />
      <QueueKpis summary={summarizeQueue(entries, now)} waitingLabel="Na fila da recepção" />
      {operation.errorMessage && <Alert tone="error">{operation.errorMessage}</Alert>}
      {operation.successMessage && <Alert tone="success">{operation.successMessage}</Alert>}
      <div className={styles.columns}>
        <Card title="Fila da recepção" icon={<ListOrdered size={20} />}>
          {queue.isLoading ? (
            <Loading />
          ) : (
            <QueueTable
              caption="Fila da recepção"
              entries={entries}
              now={now}
              showProfessional
              emptyTitle="Nenhum paciente aguardando na recepção"
              renderActions={(entry) => (
                <QueueRowActions
                  entry={entry}
                  busyKey={operation.busyKey}
                  canCall={canCall}
                  hasDestination={Boolean(destination)}
                  onCall={callTicket}
                  onForward={canForward ? forwardTicket : undefined}
                />
              )}
            />
          )}
        </Card>
        <div className={styles.stack}>
          {canCall && (
            <CallPanel
              nextEntry={nextWaitingEntry(entries)}
              destinationLabel={destination}
              now={now}
              isCalling={operation.busyKey?.startsWith('call-') ?? false}
              onCall={callTicket}
            />
          )}
          <RecentCallsCard calls={calls.data ?? []} />
        </div>
      </div>
    </>
  );
}

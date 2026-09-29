import { useCallback, useState, type ReactElement } from 'react';
import { ListOrdered } from 'lucide-react';
import { CallPanel } from '../../components/queue/CallPanel';
import { QueueKpis } from '../../components/queue/QueueKpis';
import { QueueRowActions } from '../../components/queue/QueueRowActions';
import { QueueTable } from '../../components/queue/QueueTable';
import { RecentCallsCard } from '../../components/queue/RecentCallsCard';
import { TodayBadge } from '../../components/queue/TodayBadge';
import { QUEUE_REFRESH_INTERVAL_MS } from '../../components/queue/queueRefresh';
import { Alert } from '../../components/ui/Alert';
import { Card } from '../../components/ui/Card';
import { Loading } from '../../components/ui/Loading';
import { PageHeader } from '../../components/ui/PageHeader';
import { useApiResource } from '../../hooks/useApiResource';
import { useCurrentUser } from '../../hooks/useAuth';
import { useNow } from '../../hooks/useNow';
import { useNoShowConfirmation } from '../../hooks/useNoShowConfirmation';
import { useQueueOperation } from '../../hooks/useQueueOperation';
import {
  callReceptionTicket,
  forwardToClinicalQueue,
  listRecentReceptionCalls,
  listReceptionQueue,
  markReceptionNoShow,
} from '../../services/queues';
import type { QueueEntry } from '../../types/queue';
import { resolveSelectedEntry, summarizeQueue } from '../../utils/queueMetrics';
import { hasAnyPermission } from '../../utils/userAccess';
import grid from '../../layouts/PageGrid.module.css';

const REFRESH = { refreshIntervalMs: QUEUE_REFRESH_INTERVAL_MS };

/**
 * Fila da recepção (Tela 06, somente recepção): chamada para o guichê atual,
 * rechamada e encaminhamento para a fila do profissional.
 */
export function ReceptionQueuePage(): ReactElement {
  const user = useCurrentUser();
  const now = useNow();
  const queue = useApiResource(listReceptionQueue, REFRESH);
  const calls = useApiResource(listRecentReceptionCalls, REFRESH);
  const { reload: reloadQueue } = queue;
  const { reload: reloadCalls } = calls;
  const reloadAll = useCallback(async () => {
    await Promise.all([reloadQueue(), reloadCalls()]);
  }, [reloadQueue, reloadCalls]);
  const operation = useQueueOperation(reloadAll);
  const [selectedEntryId, setSelectedEntryId] = useState<string | null>(null);
  const noShow = useNoShowConfirmation(markReceptionNoShow, operation.run, operation.busyKey);

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
        title="Fila da recepção"
        subtitle="Acompanhe a fila da recepção e realize as chamadas."
        actions={<TodayBadge now={now} />}
      />
      <QueueKpis summary={summarizeQueue(entries, now)} waitingLabel="Na fila da recepção" />
      {operation.errorMessage && <Alert tone="error">{operation.errorMessage}</Alert>}
      {operation.successMessage && <Alert tone="success">{operation.successMessage}</Alert>}
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
                onNoShow={noShow.requestNoShow}
                onForward={canForward ? forwardTicket : undefined}
              />
            )}
          />
        )}
      </Card>
      <div className={grid.pair}>
        {canCall && (
          <CallPanel
            entries={entries}
            selectedEntry={resolveSelectedEntry(entries, selectedEntryId)}
            destinationLabel={destination}
            now={now}
            isCalling={operation.busyKey?.startsWith('call-') ?? false}
            onSelect={setSelectedEntryId}
            onCall={callTicket}
          />
        )}
        <RecentCallsCard calls={calls.data ?? []} />
      </div>
      {noShow.dialog}
    </>
  );
}

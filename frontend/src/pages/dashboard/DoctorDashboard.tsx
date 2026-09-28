import { useCallback, type ReactElement } from 'react';
import { CheckCircle2, Stethoscope } from 'lucide-react';
import { Alert } from '../../components/ui/Alert';
import { Card } from '../../components/ui/Card';
import { Loading } from '../../components/ui/Loading';
import { PageHeader } from '../../components/ui/PageHeader';
import { useApiResource } from '../../hooks/useApiResource';
import { useCurrentUser } from '../../hooks/useAuth';
import { useNow } from '../../hooks/useNow';
import { useQueueOperation } from '../../hooks/useQueueOperation';
import { callClinicalTicket, completeEncounter, listClinicalQueue } from '../../services/queues';
import type { QueueEntry } from '../../types/queue';
import { nextWaitingEntry, summarizeQueue } from '../../utils/queueMetrics';
import { firstNameOf } from '../../utils/userAccess';
import { CallPanel } from './CallPanel';
import { QUEUE_REFRESH_INTERVAL_MS } from './queueRefresh';
import { QueueKpis } from './QueueKpis';
import { QueueRowActions } from './QueueRowActions';
import { QueueTable } from './QueueTable';
import { TodayBadge } from './TodayBadge';
import styles from './Dashboard.module.css';

const loadActiveQueue = (): Promise<QueueEntry[]> => listClinicalQueue('active');
const loadInactiveQueue = (): Promise<QueueEntry[]> => listClinicalQueue('inactive');

/** Visão do médico: somente a própria fila ativa e inativa (Tela 06). */
export function DoctorDashboard(): ReactElement {
  const user = useCurrentUser();
  const now = useNow();
  const refresh = { refreshIntervalMs: QUEUE_REFRESH_INTERVAL_MS };
  const active = useApiResource(loadActiveQueue, refresh);
  const inactive = useApiResource(loadInactiveQueue, refresh);
  const { reload: reloadActive } = active;
  const { reload: reloadInactive } = inactive;
  const reloadAll = useCallback(async () => {
    await Promise.all([reloadActive(), reloadInactive()]);
  }, [reloadActive, reloadInactive]);
  const operation = useQueueOperation(reloadAll);

  const activeEntries = active.data ?? [];
  const room = user.active_work_session?.station.name;

  const callTicket = (entry: QueueEntry): void =>
    void operation.run(`call-${entry.id}`, async () => {
      const call = await callClinicalTicket(entry.id);
      return `Senha ${call.ticket_code} chamada para ${call.destination_label}.`;
    });

  const completeTicket = (entry: QueueEntry): void =>
    void operation.run(`complete-${entry.id}`, async () => {
      await completeEncounter(entry.encounter_id);
      return `Atendimento da senha ${entry.ticket_code} finalizado.`;
    });

  return (
    <>
      <PageHeader
        title={`Olá, ${firstNameOf(user)}!`}
        subtitle="Sua fila de atendimento de hoje."
        actions={<TodayBadge now={now} />}
      />
      <QueueKpis summary={summarizeQueue(activeEntries, now)} waitingLabel="Na minha fila" />
      {operation.errorMessage && <Alert tone="error">{operation.errorMessage}</Alert>}
      {operation.successMessage && <Alert tone="success">{operation.successMessage}</Alert>}
      <div className={styles.columns}>
        <div className={styles.stack}>
          <Card title="Minha fila ativa" icon={<Stethoscope size={20} />}>
            {active.isLoading ? (
              <Loading />
            ) : (
              <QueueTable
                caption="Minha fila ativa"
                entries={activeEntries}
                now={now}
                emptyTitle="Nenhum paciente na sua fila"
                renderActions={(entry) => (
                  <QueueRowActions
                    entry={entry}
                    busyKey={operation.busyKey}
                    canCall
                    hasDestination={Boolean(room)}
                    onCall={callTicket}
                    onComplete={completeTicket}
                  />
                )}
              />
            )}
          </Card>
          <Card title="Atendidos hoje (fila inativa)" icon={<CheckCircle2 size={20} />}>
            <QueueTable
              caption="Fila inativa"
              entries={inactive.data ?? []}
              now={now}
              showWaitingTime={false}
              emptyTitle="Nenhum atendimento finalizado hoje"
            />
          </Card>
        </div>
        <CallPanel
          nextEntry={nextWaitingEntry(activeEntries)}
          destinationLabel={room}
          now={now}
          isCalling={operation.busyKey?.startsWith('call-') ?? false}
          onCall={callTicket}
        />
      </div>
    </>
  );
}

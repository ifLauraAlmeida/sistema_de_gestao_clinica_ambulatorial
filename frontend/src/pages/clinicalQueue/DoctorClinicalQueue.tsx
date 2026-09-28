import { useCallback, useState, type ReactElement } from 'react';
import { useLocation } from 'react-router-dom';
import { CheckCircle2, Stethoscope } from 'lucide-react';
import { CallPanel } from '../../components/queue/CallPanel';
import { QueueKpis } from '../../components/queue/QueueKpis';
import { QueueRowActions } from '../../components/queue/QueueRowActions';
import { QueueTable } from '../../components/queue/QueueTable';
import { TodayBadge } from '../../components/queue/TodayBadge';
import { QUEUE_REFRESH_INTERVAL_MS } from '../../components/queue/queueRefresh';
import { Alert } from '../../components/ui/Alert';
import { Card } from '../../components/ui/Card';
import { Loading } from '../../components/ui/Loading';
import { PageHeader } from '../../components/ui/PageHeader';
import { useApiResource } from '../../hooks/useApiResource';
import { useCurrentUser } from '../../hooks/useAuth';
import { useNow } from '../../hooks/useNow';
import { useQueueOperation } from '../../hooks/useQueueOperation';
import { callClinicalTicket, listClinicalQueue, startEncounter } from '../../services/queues';
import type { QueueEntry } from '../../types/queue';
import { resolveSelectedEntry, summarizeQueue } from '../../utils/queueMetrics';
import grid from '../../layouts/PageGrid.module.css';

const REFRESH = { refreshIntervalMs: QUEUE_REFRESH_INTERVAL_MS };
const loadActiveQueue = (): Promise<QueueEntry[]> => listClinicalQueue('active');
const loadInactiveQueue = (): Promise<QueueEntry[]> => listClinicalQueue('inactive');

/**
 * Fila clínica do médico (Tela 06): somente a própria fila ativa e inativa.
 * Chamar → iniciar atendimento → abrir atendimento/prontuário → finalizar.
 */
export function DoctorClinicalQueue(): ReactElement {
  const user = useCurrentUser();
  const now = useNow();
  const active = useApiResource(loadActiveQueue, REFRESH);
  const inactive = useApiResource(loadInactiveQueue, REFRESH);
  const { reload: reloadActive } = active;
  const { reload: reloadInactive } = inactive;
  const reloadAll = useCallback(async () => {
    await Promise.all([reloadActive(), reloadInactive()]);
  }, [reloadActive, reloadInactive]);
  const operation = useQueueOperation(reloadAll);
  const [selectedEntryId, setSelectedEntryId] = useState<string | null>(null);
  // Mensagem enviada pela tela de atendimento após a finalização.
  const flashMessage = (useLocation().state as { message?: string } | null)?.message;

  const activeEntries = active.data ?? [];
  const room = user.active_work_session?.station.name;

  const callTicket = (entry: QueueEntry): void =>
    void operation.run(`call-${entry.id}`, async () => {
      const call = await callClinicalTicket(entry.id);
      return `Senha ${call.ticket_code} chamada para ${call.destination_label}.`;
    });

  const startTicket = (entry: QueueEntry): void =>
    void operation.run(`start-${entry.id}`, async () => {
      await startEncounter(entry.encounter_id);
      return `Atendimento da senha ${entry.ticket_code} iniciado.`;
    });

  return (
    <>
      <PageHeader
        title="Minha fila clínica"
        subtitle={
          room ? `Chamadas para ${room}.` : 'Selecione um consultório para chamar pacientes.'
        }
        actions={<TodayBadge now={now} />}
      />
      <QueueKpis summary={summarizeQueue(activeEntries, now)} waitingLabel="Na minha fila" />
      {operation.errorMessage && <Alert tone="error">{operation.errorMessage}</Alert>}
      {operation.successMessage && <Alert tone="success">{operation.successMessage}</Alert>}
      {flashMessage && !operation.successMessage && <Alert tone="success">{flashMessage}</Alert>}
      <Card title="Fila ativa" icon={<Stethoscope size={20} />}>
        {active.isLoading ? (
          <Loading />
        ) : (
          <QueueTable
            caption="Fila ativa"
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
                onStart={startTicket}
                showRecordLink
              />
            )}
          />
        )}
      </Card>
      <div className={grid.pair}>
        <CallPanel
          entries={activeEntries}
          selectedEntry={resolveSelectedEntry(activeEntries, selectedEntryId)}
          destinationLabel={room}
          now={now}
          isCalling={operation.busyKey?.startsWith('call-') ?? false}
          onSelect={setSelectedEntryId}
          onCall={callTicket}
        />
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
    </>
  );
}

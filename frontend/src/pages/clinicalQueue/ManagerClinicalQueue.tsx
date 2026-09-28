import { useCallback, useState, type ReactElement } from 'react';
import { CheckCircle2, Stethoscope } from 'lucide-react';
import { QueueKpis } from '../../components/queue/QueueKpis';
import { EncounterRecordLink } from '../../components/queue/EncounterRecordLink';
import { QueueTable } from '../../components/queue/QueueTable';
import { TodayBadge } from '../../components/queue/TodayBadge';
import { QUEUE_REFRESH_INTERVAL_MS } from '../../components/queue/queueRefresh';
import { Card } from '../../components/ui/Card';
import { PageHeader } from '../../components/ui/PageHeader';
import { SelectField } from '../../components/ui/SelectField';
import { useApiResource } from '../../hooks/useApiResource';
import { useNow } from '../../hooks/useNow';
import { listProfessionals } from '../../services/agenda';
import { listClinicalQueue } from '../../services/queues';
import { summarizeQueue } from '../../utils/queueMetrics';
import { professionalOptions } from '../agenda/agendaRules';

const REFRESH = { refreshIntervalMs: QUEUE_REFRESH_INTERVAL_MS };

/** Filas clínicas de todos os profissionais, somente leitura (gestor). */
export function ManagerClinicalQueue(): ReactElement {
  const now = useNow();
  const [professionalId, setProfessionalId] = useState('');
  const professionals = useApiResource(listProfessionals).data ?? [];
  const activeLoader = useCallback(
    () => listClinicalQueue('active', professionalId || undefined),
    [professionalId],
  );
  const inactiveLoader = useCallback(
    () => listClinicalQueue('inactive', professionalId || undefined),
    [professionalId],
  );
  const active = useApiResource(activeLoader, REFRESH).data ?? [];
  const inactive = useApiResource(inactiveLoader, REFRESH).data ?? [];

  return (
    <>
      <PageHeader
        title="Filas clínicas"
        subtitle="Acompanhe as filas de todos os profissionais."
        actions={<TodayBadge now={now} />}
      />
      <Card>
        <SelectField
          label="Profissional"
          placeholder="Todos os profissionais"
          options={professionalOptions(professionals)}
          value={professionalId}
          onChange={(event) => setProfessionalId(event.target.value)}
        />
      </Card>
      <QueueKpis summary={summarizeQueue(active, now)} waitingLabel="Aguardando profissional" />
      <Card title="Filas ativas" icon={<Stethoscope size={20} />}>
        <QueueTable
          caption="Filas ativas"
          entries={active}
          now={now}
          showProfessional
          emptyTitle="Nenhum paciente aguardando"
          renderActions={(entry) => <EncounterRecordLink encounterId={entry.encounter_id} />}
        />
      </Card>
      <Card title="Atendidos hoje" icon={<CheckCircle2 size={20} />}>
        <QueueTable
          caption="Atendidos hoje"
          entries={inactive}
          now={now}
          showProfessional
          showWaitingTime={false}
          emptyTitle="Nenhum atendimento finalizado hoje"
        />
      </Card>
    </>
  );
}

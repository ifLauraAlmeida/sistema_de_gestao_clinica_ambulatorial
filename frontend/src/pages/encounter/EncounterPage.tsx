import { useCallback, useState, type ReactElement } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, ShieldAlert } from 'lucide-react';
import { Alert } from '../../components/ui/Alert';
import { Card } from '../../components/ui/Card';
import { EmptyState } from '../../components/ui/EmptyState';
import { Loading } from '../../components/ui/Loading';
import { PageHeader } from '../../components/ui/PageHeader';
import { useApiResource } from '../../hooks/useApiResource';
import { useCurrentUser } from '../../hooks/useAuth';
import { ApiError } from '../../services/api';
import { getClinicalHistory, getMedicalRecord } from '../../services/medicalRecords';
import { getProcedure } from '../../services/procedures';
import { completeEncounter, startEncounter } from '../../services/queues';
import type { HistoryEncounter, MedicalRecord } from '../../types/medicalRecord';
import { describeError } from '../../utils/errorMessages';
import { hasAnyPermission } from '../../utils/userAccess';
import grid from '../../layouts/PageGrid.module.css';
import { ClinicalHistoryCard } from './ClinicalHistoryCard';
import { ClinicalNotesCard } from './ClinicalNotesCard';
import { EncounterActions } from './EncounterActions';
import { ExecutionInfoCard } from './ExecutionInfoCard';
import { PatientHeaderCard } from './PatientHeaderCard';
import { ProcedureCard } from './ProcedureCard';
import styles from './EncounterPage.module.css';

/**
 * Atendimento (Tela 08): o que realizar, campos do procedimento e, para quem
 * tem acesso clínico, prontuário e histórico. Técnicos não carregam prontuário.
 * A autorização é sempre decidida pelo backend.
 */
export function EncounterPage(): ReactElement {
  const { encounterId = '' } = useParams();
  const user = useCurrentUser();
  const navigate = useNavigate();
  const canViewRecord = hasAnyPermission(user, [
    'medical_record.view_active_patient',
    'medical_record.view_any',
  ]);
  const procedureLoader = useCallback(() => getProcedure(encounterId), [encounterId]);
  const recordLoader = useCallback(
    (): Promise<MedicalRecord | null> =>
      canViewRecord ? getMedicalRecord(encounterId) : Promise.resolve(null),
    [encounterId, canViewRecord],
  );
  const historyLoader = useCallback(
    (): Promise<HistoryEncounter[]> =>
      canViewRecord ? getClinicalHistory(encounterId) : Promise.resolve([]),
    [encounterId, canViewRecord],
  );
  const procedure = useApiResource(procedureLoader);
  const record = useApiResource(recordLoader);
  const history = useApiResource(historyLoader);
  const [busyAction, setBusyAction] = useState<'start' | 'complete' | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function runAction(action: 'start' | 'complete'): Promise<void> {
    setBusyAction(action);
    setErrorMessage(null);
    try {
      if (action === 'start') {
        await startEncounter(encounterId);
        await procedure.reload();
      } else {
        await completeEncounter(encounterId);
        navigate('/fila-clinica', { replace: true, state: { message: 'Atendimento finalizado.' } });
      }
    } catch (error) {
      setErrorMessage(describeError(error, 'Não foi possível concluir a operação.'));
    } finally {
      setBusyAction(null);
    }
  }

  const backLink = (
    <Link to="/fila-clinica" className={styles.backLink}>
      <ArrowLeft size={18} aria-hidden="true" />
      Voltar para a fila
    </Link>
  );

  if (procedure.isLoading) return <Loading label="Abrindo atendimento…" />;
  if (!procedure.data) {
    return (
      <>
        {backLink}
        <Card>
          <EmptyState
            icon={<ShieldAlert size={24} />}
            title="Atendimento indisponível"
            description={
              procedure.error instanceof ApiError
                ? procedure.error.message
                : 'Não foi possível abrir o atendimento.'
            }
          />
        </Card>
      </>
    );
  }

  const { encounter, patient } = procedure.data;

  return (
    <>
      {backLink}
      <PageHeader
        title={canViewRecord ? 'Prontuário e atendimento' : 'Execução do atendimento'}
        subtitle={
          canViewRecord
            ? 'Registro da consulta, do procedimento e histórico clínico do paciente.'
            : 'Confira a identificação do paciente e registre o procedimento realizado.'
        }
        actions={
          <EncounterActions
            encounter={encounter}
            canStart={hasAnyPermission(user, ['encounter.start_own'])}
            canComplete={hasAnyPermission(user, ['encounter.complete_own'])}
            busyAction={busyAction}
            onStart={() => void runAction('start')}
            onComplete={() => void runAction('complete')}
          />
        }
      />
      {errorMessage && <Alert tone="error">{errorMessage}</Alert>}
      <PatientHeaderCard patient={patient} encounter={encounter} />
      <div className={grid.columns}>
        <div className={grid.stack}>
          <ProcedureCard
            key={procedure.data.recorded_at ?? 'new'}
            encounterId={encounterId}
            procedure={procedure.data}
            onSaved={() => void procedure.reload()}
          />
          {record.data && (
            <ClinicalNotesCard
              encounterId={encounterId}
              notes={record.data.clinical_notes}
              canWrite={hasAnyPermission(user, ['medical_record.update_active_patient'])}
              onSaved={record.reload}
            />
          )}
        </div>
        <div className={grid.stack}>
          <ExecutionInfoCard procedure={procedure.data} />
          {canViewRecord && <ClinicalHistoryCard history={history.data ?? []} />}
        </div>
      </div>
    </>
  );
}

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
import { completeEncounter, startEncounter } from '../../services/queues';
import { describeError } from '../../utils/errorMessages';
import { hasAnyPermission } from '../../utils/userAccess';
import grid from '../../layouts/PageGrid.module.css';
import { ClinicalHistoryCard } from './ClinicalHistoryCard';
import { ClinicalNotesCard } from './ClinicalNotesCard';
import { EncounterActions } from './EncounterActions';
import { PatientHeaderCard } from './PatientHeaderCard';
import styles from './EncounterPage.module.css';

/**
 * Prontuário e atendimento (Tela 08). Disponível enquanto o paciente está na
 * fila ativa do médico; a autorização é sempre decidida pelo backend.
 */
export function EncounterPage(): ReactElement {
  const { encounterId = '' } = useParams();
  const user = useCurrentUser();
  const navigate = useNavigate();
  const recordLoader = useCallback(() => getMedicalRecord(encounterId), [encounterId]);
  const historyLoader = useCallback(() => getClinicalHistory(encounterId), [encounterId]);
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
        await record.reload();
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

  if (record.isLoading) return <Loading label="Abrindo atendimento…" />;
  if (!record.data) {
    return (
      <>
        {backLink}
        <Card>
          <EmptyState
            icon={<ShieldAlert size={24} />}
            title="Prontuário indisponível"
            description={
              record.error instanceof ApiError
                ? record.error.message
                : 'Não foi possível abrir o atendimento.'
            }
          />
        </Card>
      </>
    );
  }

  return (
    <>
      {backLink}
      <PageHeader
        title="Prontuário e atendimento"
        subtitle="Registro da consulta e histórico clínico do paciente."
        actions={
          <EncounterActions
            encounter={record.data.encounter}
            canStart={hasAnyPermission(user, ['encounter.start_own'])}
            canComplete={hasAnyPermission(user, ['encounter.complete_own'])}
            busyAction={busyAction}
            onStart={() => void runAction('start')}
            onComplete={() => void runAction('complete')}
          />
        }
      />
      {errorMessage && <Alert tone="error">{errorMessage}</Alert>}
      <PatientHeaderCard record={record.data} />
      <div className={grid.columns}>
        <ClinicalNotesCard
          encounterId={encounterId}
          notes={record.data.clinical_notes}
          canWrite={hasAnyPermission(user, ['medical_record.update_active_patient'])}
          onSaved={record.reload}
        />
        <ClinicalHistoryCard history={history.data ?? []} />
      </div>
    </>
  );
}

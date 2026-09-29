import { useState, type FormEvent, type ReactElement } from 'react';
import { ClipboardList, Save } from 'lucide-react';
import { Alert } from '../../components/ui/Alert';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { saveProcedure } from '../../services/procedures';
import type { ProcedureView } from '../../types/procedure';
import { formatTime } from '../../utils/dateTime';
import { describeError, fieldErrorsOf } from '../../utils/errorMessages';
import { ProcedureFieldInput } from './ProcedureFieldInput';
import { toProcedureDraft, toProcedurePayload, type ProcedureDraft } from './procedureForm';
import styles from './EncounterPage.module.css';

interface ProcedureCardProps {
  encounterId: string;
  procedure: ProcedureView;
  onSaved: (procedure: ProcedureView) => void;
}

/**
 * Campos da execução do procedimento, definidos no catálogo para o serviço.
 * Cada salvamento gera nova versão no backend.
 */
export function ProcedureCard({
  encounterId,
  procedure,
  onSaved,
}: ProcedureCardProps): ReactElement | null {
  const fields = procedure.form?.fields ?? [];
  const [draft, setDraft] = useState<ProcedureDraft>(() =>
    toProcedureDraft(fields, procedure.values),
  );
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [feedback, setFeedback] = useState<{ tone: 'success' | 'error'; text: string } | null>(
    null,
  );
  const [isSaving, setSaving] = useState(false);

  if (!procedure.form) return null;

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setSaving(true);
    setFeedback(null);
    setFieldErrors({});
    try {
      onSaved(await saveProcedure(encounterId, toProcedurePayload(fields, draft)));
      setFeedback({ tone: 'success', text: 'Procedimento registrado.' });
    } catch (error) {
      setFieldErrors(fieldErrorsOf(error));
      setFeedback({ tone: 'error', text: describeError(error, 'Não foi possível registrar.') });
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card title={`Registro: ${procedure.form.name}`} icon={<ClipboardList size={20} />}>
      {procedure.recorded_at && (
        <p className={styles.noteMeta}>
          Último registro às {formatTime(procedure.recorded_at)} por {procedure.recorded_by_name}
        </p>
      )}
      <form className={styles.noteForm} onSubmit={handleSubmit} noValidate>
        {feedback && <Alert tone={feedback.tone}>{feedback.text}</Alert>}
        <div className={styles.procedureFields}>
          {fields.map((field) => (
            <ProcedureFieldInput
              key={field.key}
              field={field}
              value={draft[field.key] ?? ''}
              error={fieldErrors[field.key]}
              disabled={!procedure.can_edit}
              onChange={(value) => setDraft((current) => ({ ...current, [field.key]: value }))}
            />
          ))}
        </div>
        {procedure.can_edit && (
          <div className={styles.noteActions}>
            <Button type="submit" icon={<Save size={18} />} isLoading={isSaving}>
              Salvar registro
            </Button>
          </div>
        )}
      </form>
    </Card>
  );
}

import { useState, type FormEvent, type ReactElement } from 'react';
import { FileText, Save } from 'lucide-react';
import { Alert } from '../../components/ui/Alert';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { EmptyState } from '../../components/ui/EmptyState';
import { TextAreaField } from '../../components/ui/TextAreaField';
import { createClinicalNote } from '../../services/medicalRecords';
import type { ClinicalNote } from '../../types/medicalRecord';
import { formatTime } from '../../utils/dateTime';
import { describeError } from '../../utils/errorMessages';
import styles from './EncounterPage.module.css';

interface ClinicalNotesCardProps {
  encounterId: string;
  notes: ClinicalNote[];
  canWrite: boolean;
  onSaved: () => Promise<void>;
}

/**
 * Evoluções do atendimento atual. Evoluções não são editadas: correções são
 * registradas como nova evolução.
 */
export function ClinicalNotesCard({
  encounterId,
  notes,
  canWrite,
  onSaved,
}: ClinicalNotesCardProps): ReactElement {
  const [content, setContent] = useState('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSaving, setSaving] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setSaving(true);
    setErrorMessage(null);
    try {
      await createClinicalNote(encounterId, content.trim());
      setContent('');
      await onSaved();
    } catch (error) {
      setErrorMessage(describeError(error, 'Não foi possível salvar a evolução.'));
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card title="Atendimento" icon={<FileText size={20} />}>
      {notes.length === 0 ? (
        <EmptyState title="Nenhuma evolução registrada neste atendimento" />
      ) : (
        <ol className={styles.notes} aria-label="Evoluções deste atendimento">
          {notes.map((note) => (
            <li key={note.id} className={styles.note}>
              <span className={styles.noteMeta}>
                {formatTime(note.created_at)} • {note.author_name}
              </span>
              <p className={styles.noteContent}>{note.content}</p>
            </li>
          ))}
        </ol>
      )}
      {canWrite && (
        <form className={styles.noteForm} onSubmit={handleSubmit}>
          {errorMessage && <Alert tone="error">{errorMessage}</Alert>}
          <TextAreaField
            label="Evolução clínica"
            placeholder="Queixa, história clínica, exame, conduta e observações…"
            rows={6}
            value={content}
            onChange={(event) => setContent(event.target.value)}
          />
          <div className={styles.noteActions}>
            <Button
              type="submit"
              icon={<Save size={18} />}
              isLoading={isSaving}
              disabled={!content.trim()}
            >
              Salvar evolução
            </Button>
          </div>
        </form>
      )}
    </Card>
  );
}

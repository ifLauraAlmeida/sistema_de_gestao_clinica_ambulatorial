import type { ReactElement } from 'react';
import { History } from 'lucide-react';
import { Card } from '../../components/ui/Card';
import { EmptyState } from '../../components/ui/EmptyState';
import type { HistoryEncounter } from '../../types/medicalRecord';
import { formatIsoDate } from '../../utils/dateTime';
import styles from './EncounterPage.module.css';

/** Linha do tempo com atendimentos anteriores concluídos do paciente. */
export function ClinicalHistoryCard({ history }: { history: HistoryEncounter[] }): ReactElement {
  return (
    <Card title="Evoluções e consultas anteriores" icon={<History size={20} />}>
      {history.length === 0 ? (
        <EmptyState title="Nenhum atendimento anterior" />
      ) : (
        <ol className={styles.timeline}>
          {history.map((item) => (
            <li key={item.id} className={styles.timelineItem}>
              <div className={styles.timelineHeader}>
                <strong>{formatIsoDate(item.service_date)}</strong>
                <span>{item.specialty_name}</span>
              </div>
              <span className={styles.noteMeta}>{item.professional_name}</span>
              {item.clinical_notes.map((note) => (
                <p key={note.id} className={styles.noteContent}>
                  {note.content}
                </p>
              ))}
            </li>
          ))}
        </ol>
      )}
    </Card>
  );
}

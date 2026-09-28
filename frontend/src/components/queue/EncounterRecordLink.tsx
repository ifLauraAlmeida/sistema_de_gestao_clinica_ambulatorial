import type { ReactElement } from 'react';
import { Link } from 'react-router-dom';
import { FileText } from 'lucide-react';
import styles from './Queue.module.css';

/** Acesso à tela de atendimento/prontuário; o backend decide se o acesso é permitido. */
export function EncounterRecordLink({ encounterId }: { encounterId: string }): ReactElement {
  return (
    <Link to={`/atendimento/${encounterId}`} className={styles.recordLink}>
      <FileText size={16} aria-hidden="true" />
      Abrir atendimento
    </Link>
  );
}

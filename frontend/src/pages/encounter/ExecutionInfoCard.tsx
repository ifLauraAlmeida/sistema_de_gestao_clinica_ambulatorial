import type { ReactElement } from 'react';
import { ListChecks } from 'lucide-react';
import { Card } from '../../components/ui/Card';
import type { ProcedureView } from '../../types/procedure';
import styles from './EncounterPage.module.css';

/** Linhas exibidas apenas quando a informação existe no atendimento. */
function executionRows(procedure: ProcedureView): [string, string][] {
  const { encounter } = procedure;
  const rows: [string, string][] = [
    ['Serviço', encounter.service_name ?? encounter.specialty_name],
  ];
  if (procedure.service_type_label) rows.push(['Tipo', procedure.service_type_label]);
  if (encounter.laterality_label) rows.push(['Lateralidade', encounter.laterality_label]);
  if (encounter.with_sedation) rows.push(['Sedação', 'Sim']);
  if (procedure.laboratory_exams.length) {
    const exams = procedure.laboratory_exams.map(
      (exam) => `${exam.name} (${exam.sample_type_label})`,
    );
    rows.push(['Exames', exams.join(', ')]);
  }
  if (procedure.preparation) rows.push(['Preparo', procedure.preparation]);
  return rows;
}

/** "O que realizar": serviço, tipo, lateralidade, sedação, exames e preparo. */
export function ExecutionInfoCard({ procedure }: { procedure: ProcedureView }): ReactElement {
  return (
    <Card title="O que realizar" icon={<ListChecks size={20} />}>
      <dl className={styles.infoList}>
        {executionRows(procedure).map(([term, description]) => (
          <div key={term} className={styles.infoRow}>
            <dt>{term}</dt>
            <dd>{description}</dd>
          </div>
        ))}
      </dl>
    </Card>
  );
}

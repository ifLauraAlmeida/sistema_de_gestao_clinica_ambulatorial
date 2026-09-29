import type { ReactElement } from 'react';
import { Loading } from '../../components/ui/Loading';
import { Table } from '../../components/ui/Table';
import { useApiResource } from '../../hooks/useApiResource';
import { listLaboratoryExams } from '../../services/catalog';
import type { LaboratoryExam } from '../../types/catalog';
import styles from './CatalogPage.module.css';

function groupExams(exams: LaboratoryExam[]): [string, LaboratoryExam[]][] {
  const groups = new Map<string, LaboratoryExam[]>();
  exams.forEach((exam) => groups.set(exam.group, [...(groups.get(exam.group) ?? []), exam]));
  return [...groups];
}

/** Exames laboratoriais por grupo, com amostra, jejum e preparo. */
export function LaboratoryExamsTab(): ReactElement {
  const exams = useApiResource(listLaboratoryExams);
  if (exams.isLoading) return <Loading />;

  return (
    <div className={styles.tab}>
      <p className={styles.count}>
        {exams.data?.length ?? 0} exame(s). Solicitados no serviço "Coleta de exames laboratoriais".
      </p>
      {groupExams(exams.data ?? []).map(([group, items]) => (
        <details key={group} className={styles.area}>
          <summary>
            {group}
            <span className={styles.count}>{items.length} exame(s)</span>
          </summary>
          <Table
            caption={group}
            rows={items}
            getRowKey={(exam) => exam.id}
            columns={[
              { key: 'name', header: 'Exame', render: (e) => e.name },
              { key: 'sample', header: 'Amostra', render: (e) => e.sample_type_label },
              {
                key: 'fasting',
                header: 'Jejum',
                render: (e) => (e.fasting_hours ? `${e.fasting_hours} h` : '—'),
              },
              { key: 'preparation', header: 'Preparo', render: (e) => e.preparation || '—' },
            ]}
          />
        </details>
      ))}
    </div>
  );
}

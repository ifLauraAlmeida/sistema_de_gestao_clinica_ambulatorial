import { useState, type ReactElement } from 'react';
import { CheckboxField } from '../../components/ui/CheckboxField';
import { TextField } from '../../components/ui/TextField';
import { useApiResource } from '../../hooks/useApiResource';
import { listLaboratoryExams } from '../../services/catalog';
import type { LaboratoryExam } from '../../types/catalog';
import styles from './AgendaPage.module.css';

interface LaboratoryExamPickerProps {
  selectedIds: string[];
  error?: string;
  onChange: (ids: string[]) => void;
}

/** Seleção dos exames laboratoriais da coleta, com o maior jejum exigido. */
export function LaboratoryExamPicker({
  selectedIds,
  error,
  onChange,
}: LaboratoryExamPickerProps): ReactElement {
  const exams = useApiResource(listLaboratoryExams).data ?? [];
  const [filter, setFilter] = useState('');
  const visible = exams.filter((exam) =>
    exam.name.toLowerCase().includes(filter.trim().toLowerCase()),
  );
  const selected = exams.filter((exam) => selectedIds.includes(exam.id));
  const fasting = Math.max(0, ...selected.map((exam) => exam.fasting_hours));

  const toggle = (exam: LaboratoryExam, checked: boolean): void =>
    onChange(checked ? [...selectedIds, exam.id] : selectedIds.filter((id) => id !== exam.id));

  return (
    <fieldset className={styles.examPicker}>
      <legend>Exames laboratoriais *</legend>
      <TextField
        label="Filtrar exames"
        placeholder="Ex.: glicemia, TSH, hemograma"
        value={filter}
        onChange={(event) => setFilter(event.target.value)}
      />
      <div className={styles.examList}>
        {visible.map((exam) => (
          <CheckboxField
            key={exam.id}
            label={exam.name}
            hint={exam.fasting_hours ? `jejum ${exam.fasting_hours} h` : exam.group}
            checked={selectedIds.includes(exam.id)}
            onChange={(event) => toggle(exam, event.target.checked)}
          />
        ))}
      </div>
      <p className={styles.preparation}>
        {selected.length} exame(s) selecionado(s)
        {fasting > 0 && ` • jejum de ${fasting} horas`}
      </p>
      {error && <p className={styles.fieldError}>{error}</p>}
    </fieldset>
  );
}

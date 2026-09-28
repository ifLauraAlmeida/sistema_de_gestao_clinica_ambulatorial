import type { ReactElement } from 'react';
import { BarChart3 } from 'lucide-react';
import { Card } from '../../components/ui/Card';
import type { Appointment } from '../../types/agenda';
import { summarizeAgenda } from './agendaRules';
import styles from './AgendaPage.module.css';

export function AgendaSummaryCard({ appointments }: { appointments: Appointment[] }): ReactElement {
  const summary = summarizeAgenda(appointments);
  const items = [
    { label: 'Agendadas', value: summary.scheduled },
    { label: 'Confirmadas', value: summary.confirmed },
    { label: 'Check-in realizado', value: summary.checkedIn },
    { label: 'Faltas e cancelamentos', value: summary.absentOrCancelled },
  ];

  return (
    <Card title="Resumo do dia" icon={<BarChart3 size={20} />}>
      <ul className={styles.summary}>
        {items.map((item) => (
          <li key={item.label}>
            <span className={styles.summaryValue}>{item.value}</span>
            <span className={styles.summaryLabel}>{item.label}</span>
          </li>
        ))}
      </ul>
    </Card>
  );
}

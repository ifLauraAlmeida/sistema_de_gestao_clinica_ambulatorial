import type { ReactElement } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, MoreHorizontal, Users } from 'lucide-react';
import { Badge } from '../../components/ui/Badge';
import { Card } from '../../components/ui/Card';
import { EmptyState } from '../../components/ui/EmptyState';
import { Table } from '../../components/ui/Table';
import type { BillingEntry } from '../../types/billing';
import { formatCurrency } from '../../utils/currency';
import { BILLING_STATUS_TONES } from './billingLabels';
import styles from './FinancePage.module.css';

interface PatientsTodayCardProps {
  entries: BillingEntry[];
  selectedId: string | null;
  onSelect: (entry: BillingEntry) => void;
}

/** "Pacientes de hoje" — pagamentos e autorizações de convênio (Tela 09). */
export function PatientsTodayCard({
  entries,
  selectedId,
  onSelect,
}: PatientsTodayCardProps): ReactElement {
  return (
    <Card
      title="Pacientes de hoje"
      subtitle="Pagamentos e autorizações de convênio"
      icon={<Users size={22} />}
      actions={
        <Link to="/fila-clinica" className={styles.seeAll}>
          Ver todos os atendimentos <ArrowRight size={16} aria-hidden="true" />
        </Link>
      }
    >
      <Table
        caption="Pacientes de hoje"
        rows={entries}
        getRowKey={(entry) => entry.encounter_id}
        emptyState={<EmptyState title="Nenhum atendimento hoje" />}
        columns={[
          { key: 'position', header: '#', render: (_, index) => index + 1 },
          {
            key: 'patient',
            header: 'Paciente',
            render: (entry) => (
              <span className={entry.encounter_id === selectedId ? styles.selected : undefined}>
                {entry.patient_name}
              </span>
            ),
          },
          { key: 'payer', header: 'Convênio', render: (entry) => entry.payer_label },
          { key: 'guide', header: 'Guia', render: (entry) => entry.guide_number || '-' },
          {
            key: 'status',
            header: 'Situação',
            render: (entry) => (
              <Badge tone={BILLING_STATUS_TONES[entry.status]} withDot>
                {entry.status_label}
              </Badge>
            ),
          },
          { key: 'amount', header: 'Valor', render: (entry) => formatCurrency(entry.amount) },
          {
            key: 'actions',
            header: '',
            render: (entry) => (
              <button
                type="button"
                className={styles.rowMenu}
                onClick={() => onSelect(entry)}
                aria-label={`Registrar pagamento ou autorização de ${entry.patient_name}`}
              >
                <MoreHorizontal size={18} />
              </button>
            ),
          },
        ]}
      />
    </Card>
  );
}

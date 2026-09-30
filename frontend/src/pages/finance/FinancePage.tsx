import { useState, type ReactElement } from 'react';
import { Clock, CreditCard, FileText, ShieldCheck } from 'lucide-react';
import { TodayBadge } from '../../components/queue/TodayBadge';
import { Alert } from '../../components/ui/Alert';
import { KpiCard } from '../../components/ui/KpiCard';
import { Loading } from '../../components/ui/Loading';
import { PageHeader } from '../../components/ui/PageHeader';
import { useApiResource } from '../../hooks/useApiResource';
import { useCurrentUser } from '../../hooks/useAuth';
import { useNow } from '../../hooks/useNow';
import { getBillingDay, listInsurers } from '../../services/billing';
import type { BillingEntry } from '../../types/billing';
import { formatCurrency } from '../../utils/currency';
import { compareWithPreviousDay } from '../../utils/trend';
import { firstNameOf } from '../../utils/userAccess';
import grid from '../../layouts/PageGrid.module.css';
import { PatientsTodayCard } from './PatientsTodayCard';
import { PaymentAuthorizationCard } from './PaymentAuthorizationCard';
import styles from './FinancePage.module.css';

/** Financeiro e Autorizações (Tela 09): pagamentos e guias dos atendimentos de hoje. */
export function FinancePage(): ReactElement {
  const user = useCurrentUser();
  const now = useNow();
  const day = useApiResource(getBillingDay);
  const insurers = useApiResource(listInsurers).data ?? [];
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  if (day.isLoading || !day.data) return <Loading />;
  const { today, previous_day: yesterday, entries } = day.data;
  const selected =
    entries.find((entry) => entry.encounter_id === selectedId) ??
    entries.find((entry) => entry.status === 'PENDENTE');

  function handleSaved(entry: BillingEntry, text: string): void {
    setMessage(text);
    setSelectedId(entry.encounter_id);
    void day.reload();
  }

  return (
    <>
      <PageHeader
        title={`Olá, ${firstNameOf(user)}!`}
        subtitle="Gerencie os pagamentos e autorizações dos atendimentos de hoje."
        actions={<TodayBadge now={now} />}
      />
      <div className={grid.kpis}>
        <KpiCard
          icon={<CreditCard size={26} />}
          label="Pagamentos realizados"
          value={today.paid}
          trend={compareWithPreviousDay(today.paid, yesterday.paid, true)}
        />
        <KpiCard
          icon={<Clock size={26} />}
          label="Pagamentos pendentes"
          value={today.pending}
          tone="danger"
          trend={compareWithPreviousDay(today.pending, yesterday.pending, false)}
        />
        <KpiCard
          icon={<ShieldCheck size={26} />}
          label="Guias liberadas"
          value={today.released}
          tone="success"
          trend={compareWithPreviousDay(today.released, yesterday.released, true)}
        />
        <KpiCard
          icon={<FileText size={26} />}
          label="Valor recebido hoje"
          value={formatCurrency(today.received_amount)}
          trend={compareWithPreviousDay(
            Number(today.received_amount),
            Number(yesterday.received_amount),
            true,
          )}
        />
      </div>
      {message && <Alert tone="success">{message}</Alert>}
      <div className={`${grid.columns} ${styles.columns}`}>
        <PatientsTodayCard
          entries={entries}
          selectedId={selected?.encounter_id ?? null}
          onSelect={(entry) => setSelectedId(entry.encounter_id)}
        />
        <PaymentAuthorizationCard
          key={selected?.encounter_id ?? 'none'}
          entries={entries}
          insurers={insurers}
          selected={selected}
          onSelect={setSelectedId}
          onSaved={handleSaved}
        />
      </div>
    </>
  );
}

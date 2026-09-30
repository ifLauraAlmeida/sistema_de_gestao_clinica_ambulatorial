import { useCallback, useState, type ReactElement } from 'react';
import { Clock, CreditCard, FileText, ShieldCheck } from 'lucide-react';
import { Alert } from '../../components/ui/Alert';
import { KpiCard } from '../../components/ui/KpiCard';
import { Loading } from '../../components/ui/Loading';
import { PageHeader } from '../../components/ui/PageHeader';
import { TextField } from '../../components/ui/TextField';
import { useApiResource } from '../../hooks/useApiResource';
import { useCurrentUser } from '../../hooks/useAuth';
import { getBillingDay, listInsurers } from '../../services/billing';
import type { BillingEntry } from '../../types/billing';
import { formatCurrency } from '../../utils/currency';
import { formatIsoDate, toIsoDate } from '../../utils/dateTime';
import { compareWithPreviousDay } from '../../utils/trend';
import { firstNameOf } from '../../utils/userAccess';
import grid from '../../layouts/PageGrid.module.css';
import { PatientsTodayCard } from './PatientsTodayCard';
import { PaymentAuthorizationCard } from './PaymentAuthorizationCard';
import styles from './FinancePage.module.css';

/** Financeiro e Autorizações (Tela 09): pagamentos e guias dos atendimentos de hoje. */
export function FinancePage(): ReactElement {
  const user = useCurrentUser();
  const today = toIsoDate(new Date());
  const [date, setDate] = useState(today);
  const dayLoader = useCallback(() => getBillingDay(date), [date]);
  const day = useApiResource(dayLoader);
  const insurers = useApiResource(listInsurers).data ?? [];
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  if (day.isLoading || !day.data) return <Loading />;
  const { today: current, previous_day: yesterday, entries } = day.data;
  const isToday = date === today;
  const caption = isToday ? 'em relação a ontem' : 'em relação ao dia anterior';
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
        subtitle={
          isToday
            ? 'Gerencie os pagamentos e autorizações dos atendimentos de hoje.'
            : `Pagamentos e autorizações dos atendimentos de ${formatIsoDate(date)}.`
        }
        actions={
          <TextField
            label="Data"
            type="date"
            value={date}
            max={today}
            onChange={(event) => {
              if (!event.target.value) return;
              setDate(event.target.value);
              setSelectedId(null);
              setMessage(null);
            }}
          />
        }
      />
      <div className={grid.kpis}>
        <KpiCard
          icon={<CreditCard size={26} />}
          label="Pagamentos realizados"
          value={current.paid}
          trend={compareWithPreviousDay(current.paid, yesterday.paid, true, caption)}
        />
        <KpiCard
          icon={<Clock size={26} />}
          label="Pagamentos pendentes"
          value={current.pending}
          tone="danger"
          trend={compareWithPreviousDay(current.pending, yesterday.pending, false, caption)}
        />
        <KpiCard
          icon={<ShieldCheck size={26} />}
          label="Guias liberadas"
          value={current.released}
          tone="success"
          trend={compareWithPreviousDay(current.released, yesterday.released, true, caption)}
        />
        <KpiCard
          icon={<FileText size={26} />}
          label={isToday ? 'Valor recebido hoje' : 'Valor recebido no dia'}
          value={formatCurrency(current.received_amount)}
          trend={compareWithPreviousDay(
            Number(current.received_amount),
            Number(yesterday.received_amount),
            true,
            caption,
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

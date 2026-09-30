import { useState, type ReactElement } from 'react';
import { CreditCard, ShieldCheck } from 'lucide-react';
import { Alert } from '../../components/ui/Alert';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { SelectField } from '../../components/ui/SelectField';
import { TextField } from '../../components/ui/TextField';
import { confirmPayment, releaseAuthorization } from '../../services/billing';
import type { BillingEntry, HealthInsurer, PaymentMethod } from '../../types/billing';
import { parseCurrencyInput, toCurrencyInput } from '../../utils/currency';
import { describeError, fieldErrorsOf } from '../../utils/errorMessages';
import { PARTICULAR, PAYMENT_METHOD_OPTIONS } from './billingLabels';
import styles from './FinancePage.module.css';

interface PaymentAuthorizationCardProps {
  entries: BillingEntry[];
  insurers: HealthInsurer[];
  selected: BillingEntry | undefined;
  onSelect: (encounterId: string) => void;
  onSaved: (entry: BillingEntry, message: string) => void;
}

/**
 * "Pagamento e Autorização" (Tela 09): confirma pagamento ou libera o
 * atendimento pela guia do convênio.
 */
export function PaymentAuthorizationCard({
  entries,
  insurers,
  selected,
  onSelect,
  onSaved,
}: PaymentAuthorizationCardProps): ReactElement {
  const [insurerId, setInsurerId] = useState(selected?.insurer_id ?? PARTICULAR);
  const [guideNumber, setGuideNumber] = useState(selected?.guide_number ?? '');
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>(
    selected?.payment_method || 'CARTAO_CREDITO',
  );
  const [amountText, setAmountText] = useState(toCurrencyInput(selected?.amount ?? null));
  const [busy, setBusy] = useState<'payment' | 'authorization' | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const amount = parseCurrencyInput(amountText);
  const canRelease = Boolean(selected && insurerId && guideNumber.trim() && amount);

  async function run(kind: 'payment' | 'authorization'): Promise<void> {
    if (!selected || !amount) return;
    setBusy(kind);
    setErrorMessage(null);
    setFieldErrors({});
    try {
      const saved =
        kind === 'payment'
          ? await confirmPayment(selected.encounter_id, {
              insurer: insurerId || null,
              guide_number: guideNumber.trim(),
              payment_method: paymentMethod,
              amount,
            })
          : await releaseAuthorization(selected.encounter_id, {
              insurer: insurerId,
              guide_number: guideNumber.trim(),
              amount,
            });
      const action = kind === 'payment' ? 'Pagamento confirmado' : 'Atendimento liberado';
      onSaved(saved, `${action}: ${saved.patient_name}.`);
    } catch (error) {
      setFieldErrors(fieldErrorsOf(error));
      setErrorMessage(describeError(error, 'Não foi possível registrar.'));
    } finally {
      setBusy(null);
    }
  }

  return (
    <Card
      title="Pagamento e Autorização"
      subtitle="Registre o pagamento ou libere o atendimento"
      icon={<CreditCard size={22} />}
    >
      <div className={styles.form}>
        {errorMessage && <Alert tone="error">{errorMessage}</Alert>}
        <SelectField
          label="Paciente"
          value={selected?.encounter_id ?? ''}
          placeholder="Selecione o paciente"
          options={entries.map((entry) => ({
            value: entry.encounter_id,
            label: `${entry.patient_name} (${entry.ticket_code})`,
          }))}
          onChange={(event) => onSelect(event.target.value)}
        />
        <SelectField
          label="Convênio"
          value={insurerId}
          options={[
            { value: PARTICULAR, label: 'Particular' },
            ...insurers.map((insurer) => ({ value: insurer.id, label: insurer.name })),
          ]}
          onChange={(event) => setInsurerId(event.target.value)}
          error={fieldErrors.insurer}
        />
        <TextField
          label="Número da guia"
          value={guideNumber}
          disabled={!insurerId}
          onChange={(event) => setGuideNumber(event.target.value)}
          error={fieldErrors.guide_number}
        />
        <SelectField
          label="Forma de pagamento"
          value={paymentMethod}
          options={PAYMENT_METHOD_OPTIONS}
          onChange={(event) => setPaymentMethod(event.target.value as PaymentMethod)}
          error={fieldErrors.payment_method}
        />
        <TextField
          label="Valor (R$)"
          inputMode="decimal"
          value={amountText}
          onChange={(event) => setAmountText(event.target.value)}
          error={
            amountText && !amount ? 'Informe um valor válido, ex.: 420,00' : fieldErrors.amount
          }
        />
        <Button
          size="lg"
          fullWidth
          icon={<CreditCard size={20} />}
          disabled={!selected || !amount}
          isLoading={busy === 'payment'}
          onClick={() => void run('payment')}
        >
          Confirmar pagamento
        </Button>
        <Button
          size="lg"
          fullWidth
          variant="secondary"
          className={styles.releaseButton}
          icon={<ShieldCheck size={20} />}
          disabled={!canRelease}
          title={canRelease ? undefined : 'Informe convênio e número da guia para liberar'}
          isLoading={busy === 'authorization'}
          onClick={() => void run('authorization')}
        >
          Liberar atendimento
        </Button>
      </div>
    </Card>
  );
}

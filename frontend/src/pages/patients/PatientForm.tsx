import { useState, type FormEvent, type ReactElement } from 'react';
import { Save, UserPlus, X } from 'lucide-react';
import { Alert } from '../../components/ui/Alert';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { TextAreaField } from '../../components/ui/TextAreaField';
import { TextField } from '../../components/ui/TextField';
import { createPatient, updatePatient } from '../../services/patients';
import type { PatientDemographics, PatientDemographicsInput } from '../../types/patient';
import { describeError, fieldErrorsOf } from '../../utils/errorMessages';
import { emptyPatientInput, toPatientInput, toPatientPayload } from './patientFormState';
import styles from './PatientsPage.module.css';

interface FieldBinding {
  value: string;
  error: string | undefined;
  onChange: (event: { target: { value: string } }) => void;
}

interface PatientFormProps {
  patient: PatientDemographics | null;
  onSaved: (patient: PatientDemographics, wasCreated: boolean) => void;
  onClose: () => void;
}

/** Cadastro e edição dos dados cadastrais permitidos à recepção. */
export function PatientForm({ patient, onSaved, onClose }: PatientFormProps): ReactElement {
  const [values, setValues] = useState<PatientDemographicsInput>(() =>
    patient ? toPatientInput(patient) : emptyPatientInput(),
  );
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSaving, setSaving] = useState(false);

  const bind = (field: keyof PatientDemographicsInput): FieldBinding => ({
    value: values[field] ?? '',
    error: fieldErrors[field],
    onChange: (event: { target: { value: string } }) =>
      setValues((current) => ({ ...current, [field]: event.target.value })),
  });

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setSaving(true);
    setErrorMessage(null);
    setFieldErrors({});
    try {
      const payload = toPatientPayload(values);
      const saved = patient
        ? await updatePatient(patient.id, payload)
        : await createPatient(payload);
      onSaved(saved, patient === null);
    } catch (error) {
      setFieldErrors(fieldErrorsOf(error));
      setErrorMessage(describeError(error, 'Não foi possível salvar o cadastro.'));
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card
      title={patient ? 'Editar paciente' : 'Novo paciente'}
      icon={<UserPlus size={20} />}
      actions={
        <Button
          variant="ghost"
          icon={<X size={18} />}
          onClick={onClose}
          aria-label="Fechar formulário"
        >
          Fechar
        </Button>
      }
    >
      <form className={styles.form} onSubmit={handleSubmit} noValidate>
        {errorMessage && <Alert tone="error">{errorMessage}</Alert>}
        <TextField label="Nome completo *" required autoFocus {...bind('full_name')} />
        <TextField label="Nome social" {...bind('social_name')} />
        <div className={styles.formRow}>
          <TextField label="CPF" placeholder="000.000.000-00" {...bind('cpf')} />
          <TextField label="Data de nascimento *" type="date" required {...bind('birth_date')} />
        </div>
        <TextField label="Telefone" placeholder="(00) 00000-0000" {...bind('phone')} />
        <TextField label="Nome da mãe" {...bind('mother_name')} />
        <TextAreaField label="Observações administrativas" {...bind('administrative_notes')} />
        <div className={styles.formActions}>
          <Button variant="secondary" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit" icon={<Save size={18} />} isLoading={isSaving}>
            Salvar cadastro
          </Button>
        </div>
      </form>
    </Card>
  );
}

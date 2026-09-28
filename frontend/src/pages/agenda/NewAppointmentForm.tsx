import { useState, type FormEvent, type ReactElement } from 'react';
import { CalendarPlus, Search, X } from 'lucide-react';
import { Alert } from '../../components/ui/Alert';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { SelectField } from '../../components/ui/SelectField';
import { TextAreaField } from '../../components/ui/TextAreaField';
import { TextField } from '../../components/ui/TextField';
import { createAppointment } from '../../services/agenda';
import { searchPatients } from '../../services/patients';
import type { Appointment, Professional } from '../../types/agenda';
import type { PatientListItem } from '../../types/patient';
import { combineLocalDateTime } from '../../utils/dateTime';
import { describeError, fieldErrorsOf } from '../../utils/errorMessages';
import { professionalOptions, specialtyOptions } from './agendaRules';
import styles from './AgendaPage.module.css';

interface NewAppointmentFormProps {
  professionals: Professional[];
  defaultDate: string;
  onCreated: (appointment: Appointment) => void;
  onClose: () => void;
}

/** Agendamento de consulta: localizar paciente, escolher profissional, especialidade e horário. */
export function NewAppointmentForm({
  professionals,
  defaultDate,
  onCreated,
  onClose,
}: NewAppointmentFormProps): ReactElement {
  const [patientSearch, setPatientSearch] = useState('');
  const [patients, setPatients] = useState<PatientListItem[] | null>(null);
  const [patientId, setPatientId] = useState('');
  const [professionalId, setProfessionalId] = useState('');
  const [specialtyId, setSpecialtyId] = useState('');
  const [date, setDate] = useState(defaultDate);
  const [time, setTime] = useState('');
  const [notes, setNotes] = useState('');
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSaving, setSaving] = useState(false);

  async function findPatients(): Promise<void> {
    const page = await searchPatients(patientSearch.trim());
    setPatients(page.results);
    setPatientId(page.results[0]?.id ?? '');
  }

  function selectProfessional(id: string): void {
    setProfessionalId(id);
    setSpecialtyId(specialtyOptions(professionals, id)[0]?.value ?? '');
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setSaving(true);
    setErrorMessage(null);
    setFieldErrors({});
    try {
      const appointment = await createAppointment({
        patient: patientId,
        professional: professionalId,
        specialty: specialtyId,
        scheduled_for: date && time ? combineLocalDateTime(date, time) : '',
        notes,
      });
      onCreated(appointment);
    } catch (error) {
      setFieldErrors(fieldErrorsOf(error));
      setErrorMessage(describeError(error, 'Não foi possível criar o agendamento.'));
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card
      title="Novo agendamento"
      icon={<CalendarPlus size={20} />}
      actions={
        <Button variant="ghost" icon={<X size={18} />} onClick={onClose}>
          Fechar
        </Button>
      }
    >
      <form className={styles.form} onSubmit={handleSubmit} noValidate>
        {errorMessage && <Alert tone="error">{errorMessage}</Alert>}
        <div className={styles.inline}>
          <TextField
            label="Localizar paciente"
            placeholder="Nome, CPF ou telefone"
            value={patientSearch}
            onChange={(event) => setPatientSearch(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter') {
                event.preventDefault();
                void findPatients();
              }
            }}
          />
          <Button
            variant="secondary"
            icon={<Search size={16} />}
            onClick={() => void findPatients()}
          >
            Buscar
          </Button>
        </div>
        {patients && (
          <SelectField
            label="Paciente *"
            value={patientId}
            onChange={(event) => setPatientId(event.target.value)}
            placeholder={patients.length ? undefined : 'Nenhum paciente encontrado'}
            options={patients.map((p) => ({
              value: p.id,
              label: `${p.full_name} (${p.cpf_masked || 'sem CPF'})`,
            }))}
            error={fieldErrors.patient}
          />
        )}
        <SelectField
          label="Profissional *"
          value={professionalId}
          placeholder="Selecione o profissional"
          options={professionalOptions(professionals)}
          onChange={(event) => selectProfessional(event.target.value)}
          error={fieldErrors.professional}
        />
        <SelectField
          label="Especialidade *"
          value={specialtyId}
          placeholder="Selecione a especialidade"
          options={specialtyOptions(professionals, professionalId || undefined)}
          onChange={(event) => setSpecialtyId(event.target.value)}
          error={fieldErrors.specialty}
        />
        <div className={styles.inline}>
          <TextField
            label="Data *"
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
          />
          <TextField
            label="Horário *"
            type="time"
            value={time}
            onChange={(e) => setTime(e.target.value)}
            error={fieldErrors.scheduled_for}
          />
        </div>
        <TextAreaField
          label="Observações"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />
        <div className={styles.formActions}>
          <Button variant="secondary" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit" isLoading={isSaving} disabled={!patientId || !professionalId}>
            Agendar consulta
          </Button>
        </div>
      </form>
    </Card>
  );
}

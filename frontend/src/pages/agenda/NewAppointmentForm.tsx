import { useState, type FormEvent, type ReactElement } from 'react';
import { CalendarPlus, Search, X } from 'lucide-react';
import { Alert } from '../../components/ui/Alert';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { CheckboxField } from '../../components/ui/CheckboxField';
import { SelectField } from '../../components/ui/SelectField';
import { TextAreaField } from '../../components/ui/TextAreaField';
import { TextField } from '../../components/ui/TextField';
import { createAppointment } from '../../services/agenda';
import { searchPatients } from '../../services/patients';
import type { Appointment, Laterality, Professional } from '../../types/agenda';
import type { CatalogService } from '../../types/catalog';
import type { PatientListItem } from '../../types/patient';
import { combineLocalDateTime } from '../../utils/dateTime';
import { describeError, fieldErrorsOf } from '../../utils/errorMessages';
import { LATERALITY_OPTIONS, professionalOptions, professionalsForService } from './agendaRules';
import { LaboratoryExamPicker } from './LaboratoryExamPicker';
import { ServicePicker } from './ServicePicker';
import styles from './AgendaPage.module.css';

interface NewAppointmentFormProps {
  professionals: Professional[];
  defaultDate: string;
  onCreated: (appointment: Appointment) => void;
  onClose: () => void;
}

/** Agendamento de um serviço do catálogo: paciente, serviço, opções, profissional e horário. */
export function NewAppointmentForm({
  professionals,
  defaultDate,
  onCreated,
  onClose,
}: NewAppointmentFormProps): ReactElement {
  const [patientSearch, setPatientSearch] = useState('');
  const [patients, setPatients] = useState<PatientListItem[] | null>(null);
  const [patientId, setPatientId] = useState('');
  const [service, setService] = useState<CatalogService | undefined>();
  const [professionalId, setProfessionalId] = useState('');
  const [laterality, setLaterality] = useState<Laterality | ''>('');
  const [withSedation, setWithSedation] = useState(false);
  const [examIds, setExamIds] = useState<string[]>([]);
  const [date, setDate] = useState(defaultDate);
  const [time, setTime] = useState('');
  const [notes, setNotes] = useState('');
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSaving, setSaving] = useState(false);
  const eligibleProfessionals = professionalsForService(professionals, service);

  async function findPatients(): Promise<void> {
    const page = await searchPatients(patientSearch.trim());
    setPatients(page.results);
    setPatientId(page.results[0]?.id ?? '');
  }

  function selectService(selected: CatalogService | undefined): void {
    setService(selected);
    setLaterality('');
    setWithSedation(false);
    setExamIds([]);
    setProfessionalId(professionalsForService(professionals, selected)[0]?.id ?? '');
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
        service: service?.id ?? '',
        laterality,
        with_sedation: withSedation,
        laboratory_exams: examIds,
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
        <ServicePicker selected={service} error={fieldErrors.service} onSelect={selectService} />
        {service && (
          <>
            <SelectField
              label="Profissional *"
              value={professionalId}
              placeholder={
                eligibleProfessionals.length ? undefined : 'Nenhum profissional cadastrado'
              }
              options={professionalOptions(eligibleProfessionals)}
              onChange={(event) => setProfessionalId(event.target.value)}
              error={fieldErrors.professional}
            />
            {service.requires_laterality && (
              <SelectField
                label="Lateralidade *"
                value={laterality}
                placeholder="Selecione o lado"
                options={LATERALITY_OPTIONS}
                onChange={(event) => setLaterality(event.target.value as Laterality | '')}
                error={fieldErrors.laterality}
              />
            )}
            {service.allows_sedation && (
              <CheckboxField
                label="Com sedação"
                checked={withSedation}
                onChange={(event) => setWithSedation(event.target.checked)}
              />
            )}
            {service.is_laboratory_collection && (
              <LaboratoryExamPicker
                selectedIds={examIds}
                onChange={setExamIds}
                error={fieldErrors.laboratory_exams}
              />
            )}
          </>
        )}
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
          <Button
            type="submit"
            isLoading={isSaving}
            disabled={!patientId || !service || !professionalId}
          >
            Agendar
          </Button>
        </div>
      </form>
    </Card>
  );
}

import type { ReactElement } from 'react';
import { CalendarDays, Stethoscope, Ticket, UserRound } from 'lucide-react';
import { Badge } from '../../components/ui/Badge';
import type { EncounterSummary, PatientSummary } from '../../types/medicalRecord';
import { serviceWithLaterality } from '../../utils/serviceLabels';
import { formatIsoDate } from '../../utils/dateTime';
import styles from './EncounterPage.module.css';

/** Identificação do paciente e do atendimento no topo do prontuário. */
export function PatientHeaderCard({
  patient,
  encounter,
}: {
  patient: PatientSummary;
  encounter: EncounterSummary;
}): ReactElement {
  const facts = [
    {
      icon: <CalendarDays size={22} />,
      label: 'Idade',
      value: `${patient.age} anos`,
      detail: formatIsoDate(patient.birth_date),
    },
    {
      icon: <Stethoscope size={22} />,
      label: 'Serviço',
      value: encounter.service_name
        ? serviceWithLaterality(encounter.service_name, encounter.laterality_label)
        : encounter.specialty_name,
    },
    { icon: <Ticket size={22} />, label: 'Senha', value: encounter.ticket_code },
  ];

  return (
    <section className={styles.patientHeader} aria-label="Paciente em atendimento">
      <div className={styles.patientIdentity}>
        <span className={styles.avatar} aria-hidden="true">
          <UserRound size={34} />
        </span>
        <div>
          <h2 className={styles.patientName}>{patient.display_name}</h2>
          <Badge tone={encounter.status === 'EM_ATENDIMENTO' ? 'success' : 'warning'}>
            {encounter.status_label}
          </Badge>
        </div>
      </div>
      {facts.map((fact) => (
        <div key={fact.label} className={styles.fact}>
          <span className={styles.factIcon} aria-hidden="true">
            {fact.icon}
          </span>
          <div>
            <span className={styles.factLabel}>{fact.label}</span>
            <strong className={styles.factValue}>{fact.value}</strong>
            {fact.detail && <span className={styles.factLabel}>{fact.detail}</span>}
          </div>
        </div>
      ))}
    </section>
  );
}

import type { PatientDemographics, PatientDemographicsInput } from '../../types/patient';

export function emptyPatientInput(): PatientDemographicsInput {
  return {
    full_name: '',
    social_name: '',
    cpf: '',
    birth_date: '',
    phone: '',
    mother_name: '',
    administrative_notes: '',
  };
}

/** Converte o cadastro da API nos campos editáveis do formulário. */
export function toPatientInput(patient: PatientDemographics): PatientDemographicsInput {
  return {
    full_name: patient.full_name,
    social_name: patient.social_name,
    cpf: patient.cpf ?? '',
    birth_date: patient.birth_date,
    phone: patient.phone,
    mother_name: patient.mother_name,
    administrative_notes: patient.administrative_notes,
  };
}

/** CPF vazio é enviado como nulo (paciente sem CPF informado). */
export function toPatientPayload(input: PatientDemographicsInput): PatientDemographicsInput {
  return { ...input, full_name: input.full_name.trim(), cpf: input.cpf?.trim() || null };
}

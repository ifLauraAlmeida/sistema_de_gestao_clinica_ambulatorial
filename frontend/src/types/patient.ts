/** Paciente em listagens: CPF sempre mascarado. */
export interface PatientListItem {
  id: string;
  full_name: string;
  social_name: string;
  cpf_masked: string;
  birth_date: string;
  phone: string;
  is_active: boolean;
}

/** Campos cadastrais editáveis pela recepção. */
export interface PatientDemographicsInput {
  full_name: string;
  social_name: string;
  cpf: string | null;
  birth_date: string;
  phone: string;
  mother_name: string;
  administrative_notes: string;
}

export interface PatientDemographics extends PatientDemographicsInput {
  id: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

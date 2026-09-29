export type ServiceType = 'CONSULTA' | 'SESSAO' | 'PROCEDIMENTO' | 'EXAME';

/** Serviço agendável do catálogo (consulta, sessão, procedimento ou exame). */
export interface CatalogService {
  id: string;
  name: string;
  service_type: ServiceType;
  service_type_label: string;
  duration_minutes: number;
  requires_laterality: boolean;
  allows_sedation: boolean;
  is_laboratory_collection: boolean;
  preparation_instructions: string;
  specialty_id: string;
  specialty_name: string;
  group_name: string;
  category_name: string;
  aliases: string[];
  has_execution_form: boolean;
}

export interface CatalogGroup {
  id: string;
  name: string;
  services: CatalogService[];
}

export interface CatalogCategory {
  id: string;
  name: string;
  groups: CatalogGroup[];
}

export interface LaboratoryExam {
  id: string;
  name: string;
  group: string;
  sample_type: string;
  sample_type_label: string;
  preparation: string;
  fasting_hours: number;
}

export interface ServicePackage {
  id: string;
  name: string;
  description: string;
  items: { id: string; name: string; kind: 'SERVICE' | 'LABORATORY_EXAM' }[];
}

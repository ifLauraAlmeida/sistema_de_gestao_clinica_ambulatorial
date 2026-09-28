import type { Paginated } from '../types/pagination';
import type {
  PatientDemographics,
  PatientDemographicsInput,
  PatientListItem,
} from '../types/patient';
import { apiClient, withQuery } from './api';

export function searchPatients(search: string, page = 1): Promise<Paginated<PatientListItem>> {
  return apiClient.get(withQuery('/patients/', { search, page }));
}

export function getPatient(patientId: string): Promise<PatientDemographics> {
  return apiClient.get(`/patients/${patientId}/`);
}

export function createPatient(input: PatientDemographicsInput): Promise<PatientDemographics> {
  return apiClient.post('/patients/', input);
}

export function updatePatient(
  patientId: string,
  input: PatientDemographicsInput,
): Promise<PatientDemographics> {
  return apiClient.patch(`/patients/${patientId}/`, input);
}

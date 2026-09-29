import type {
  CatalogCategory,
  CatalogService,
  LaboratoryExam,
  ServicePackage,
} from '../types/catalog';
import { apiClient, withQuery } from './api';

export function getCatalogTree(): Promise<CatalogCategory[]> {
  return apiClient.get('/catalog/');
}

/** Busca por nome ou sinônimo (ex.: "ergometria" encontra "Teste ergométrico"). */
export function searchServices(search: string): Promise<CatalogService[]> {
  return apiClient.get(withQuery('/catalog/services/', { search }));
}

export function listLaboratoryExams(): Promise<LaboratoryExam[]> {
  return apiClient.get('/catalog/laboratory-exams/');
}

export function listServicePackages(): Promise<ServicePackage[]> {
  return apiClient.get('/catalog/packages/');
}

import type {
  AuthorizationInput,
  BillingDay,
  BillingEntry,
  HealthInsurer,
  PaymentInput,
} from '../types/billing';
import { apiClient, withQuery } from './api';

/** Financeiro de uma data ("2026-09-29"); sem data, o dia atual. */
export function getBillingDay(date?: string): Promise<BillingDay> {
  return apiClient.get(withQuery('/billing/day/', { date }));
}

export function listInsurers(): Promise<HealthInsurer[]> {
  return apiClient.get('/billing/insurers/');
}

export function confirmPayment(encounterId: string, input: PaymentInput): Promise<BillingEntry> {
  return apiClient.post(`/billing/encounters/${encounterId}/payment/`, input);
}

/** Libera o atendimento pela guia autorizada do convênio. */
export function releaseAuthorization(
  encounterId: string,
  input: AuthorizationInput,
): Promise<BillingEntry> {
  return apiClient.post(`/billing/encounters/${encounterId}/authorization/`, input);
}

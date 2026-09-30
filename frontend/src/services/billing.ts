import type {
  AuthorizationInput,
  BillingDay,
  BillingEntry,
  HealthInsurer,
  PaymentInput,
} from '../types/billing';
import { apiClient } from './api';

export function getBillingDay(): Promise<BillingDay> {
  return apiClient.get('/billing/day/');
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

export type AuditMetadataValue = string | number | boolean | null;

export interface AuditEvent {
  id: string;
  timestamp: string;
  action: string;
  action_label: string;
  category: string | null;
  category_label: string | null;
  is_denial: boolean;
  reason_label: string | null;
  user: { id: string; username: string; display_name: string; role_label: string } | null;
  entity_type: string;
  entity_id: string;
  entity_label: string | null;
  ip_address: string | null;
  metadata: Record<string, AuditMetadataValue>;
}

export interface AuditSummary {
  today: { total: number; denied: number; medical_records_opened: number; failed_logins: number };
  categories: { value: string; label: string }[];
  users: { id: string; display_name: string; role_label: string }[];
}

export interface AuditQuery {
  date_from: string;
  date_to: string;
  user?: string;
  category?: string;
  outcome?: 'denied' | 'granted';
  search?: string;
  page: number;
}

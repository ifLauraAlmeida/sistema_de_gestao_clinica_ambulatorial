import type { ReactElement } from 'react';
import { Phone } from 'lucide-react';
import styles from './PhoneLink.module.css';

/**
 * Telefone do paciente como link `tel:` (abre discador/softphone quando houver).
 * Exibe "—" quando o cadastro não tem telefone.
 */
export function PhoneLink({ phone }: { phone: string }): ReactElement {
  if (!phone) return <span>—</span>;
  const digits = phone.replace(/\D/g, '');
  return (
    <a href={`tel:${digits}`} className={styles.link} aria-label={`Ligar para ${phone}`}>
      <Phone size={14} aria-hidden="true" />
      {phone}
    </a>
  );
}

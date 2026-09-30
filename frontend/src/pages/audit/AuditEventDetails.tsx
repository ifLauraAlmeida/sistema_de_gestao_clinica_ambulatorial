import type { ReactElement } from 'react';
import { FileSearch, X } from 'lucide-react';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import type { AuditEvent } from '../../types/audit';
import { describeMetadata } from './metadataLabels';
import styles from './AuditPage.module.css';

const dateTimeFormatter = new Intl.DateTimeFormat('pt-BR', {
  dateStyle: 'short',
  timeStyle: 'medium',
});

/** Detalhe do evento: quem, o quê, quando, onde, motivo e estados anterior/novo. */
export function AuditEventDetails({
  event,
  onClose,
}: {
  event: AuditEvent;
  onClose: () => void;
}): ReactElement {
  const rows: [string, string][] = [
    ['Data e hora', dateTimeFormatter.format(new Date(event.timestamp))],
    ['Usuário', event.user ? `${event.user.display_name} (${event.user.role_label})` : '—'],
    ['Categoria', event.category_label ?? '—'],
    ['Afetado', event.entity_label ?? (event.entity_id || '—')],
    ...(event.reason_label ? ([['Motivo', event.reason_label]] as [string, string][]) : []),
    ['IP', event.ip_address ?? '—'],
    ...describeMetadata(event.metadata),
  ];

  return (
    <Card
      title="Detalhes do evento"
      icon={<FileSearch size={20} />}
      actions={
        <Button variant="ghost" icon={<X size={18} />} onClick={onClose}>
          Fechar
        </Button>
      }
    >
      <Badge tone={event.is_denial ? 'danger' : 'info'} withDot>
        {event.action_label}
      </Badge>
      <dl className={styles.detailList}>
        {rows.map(([term, description]) => (
          <div key={term} className={styles.detailRow}>
            <dt>{term}</dt>
            <dd>{description}</dd>
          </div>
        ))}
      </dl>
      <p className={styles.immutable}>
        Registro imutável: não pode ser alterado nem apagado. Conteúdo clínico, senhas e CPF
        completo nunca são gravados na auditoria.
      </p>
    </Card>
  );
}

import { useCallback, useState, type ReactElement } from 'react';
import {
  Activity,
  ChevronLeft,
  ChevronRight,
  Download,
  FileText,
  ShieldAlert,
  UserX,
} from 'lucide-react';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { EmptyState } from '../../components/ui/EmptyState';
import { KpiCard } from '../../components/ui/KpiCard';
import { Loading } from '../../components/ui/Loading';
import { PageHeader } from '../../components/ui/PageHeader';
import { Table } from '../../components/ui/Table';
import { useApiResource } from '../../hooks/useApiResource';
import { auditExportUrl, getAuditSummary, listAuditEvents } from '../../services/audit';
import type { AuditEvent, AuditQuery } from '../../types/audit';
import { toIsoDate } from '../../utils/dateTime';
import grid from '../../layouts/PageGrid.module.css';
import { AuditEventDetails } from './AuditEventDetails';
import { AuditFiltersCard } from './AuditFiltersCard';
import styles from './AuditPage.module.css';

const timeFormatter = new Intl.DateTimeFormat('pt-BR', {
  day: '2-digit',
  month: '2-digit',
  hour: '2-digit',
  minute: '2-digit',
  second: '2-digit',
});

function initialQuery(): AuditQuery {
  const today = toIsoDate(new Date());
  return { date_from: today, date_to: today, page: 1 };
}

/** Auditoria (gestor): quem fez o quê, quando e de onde, com filtros e exportação. */
export function AuditPage(): ReactElement {
  const [query, setQuery] = useState<AuditQuery>(initialQuery);
  const [selected, setSelected] = useState<AuditEvent | null>(null);
  const summary = useApiResource(getAuditSummary);
  const loader = useCallback(() => listAuditEvents(query), [query]);
  const events = useApiResource(loader);
  const today = summary.data?.today;
  const page = events.data;

  return (
    <>
      <PageHeader
        title="Auditoria"
        subtitle="Rastreabilidade de acessos e operações. Os registros não podem ser alterados nem apagados."
        actions={
          <a className={styles.exportLink} href={auditExportUrl(query)} download>
            <Download size={18} aria-hidden="true" />
            Exportar CSV
          </a>
        }
      />
      <div className={grid.kpis}>
        <KpiCard icon={<Activity size={26} />} label="Eventos hoje" value={today?.total ?? '—'} />
        <KpiCard
          icon={<ShieldAlert size={26} />}
          label="Acessos negados hoje"
          value={today?.denied ?? '—'}
          tone={today?.denied ? 'danger' : 'info'}
        />
        <KpiCard
          icon={<FileText size={26} />}
          label="Prontuários abertos hoje"
          value={today?.medical_records_opened ?? '—'}
          tone="success"
        />
        <KpiCard
          icon={<UserX size={26} />}
          label="Logins com falha hoje"
          value={today?.failed_logins ?? '—'}
          tone={today?.failed_logins ? 'danger' : 'info'}
        />
      </div>
      <AuditFiltersCard query={query} summary={summary.data} onChange={setQuery} />
      <div className={selected ? grid.columns : undefined}>
        <Card title="Eventos" subtitle={page ? `${page.count} evento(s) encontrados` : undefined}>
          {events.isLoading && <Loading />}
          {page && (
            <>
              <Table
                caption="Eventos de auditoria"
                rows={page.results}
                getRowKey={(event) => event.id}
                emptyState={<EmptyState title="Nenhum evento para os filtros escolhidos" />}
                columns={[
                  {
                    key: 'time',
                    header: 'Data e hora',
                    render: (e) => timeFormatter.format(new Date(e.timestamp)),
                  },
                  {
                    key: 'user',
                    header: 'Usuário',
                    render: (e) =>
                      e.user ? (
                        <span className={styles.userCell}>
                          {e.user.display_name}
                          <small>{e.user.role_label}</small>
                        </span>
                      ) : (
                        '—'
                      ),
                  },
                  {
                    key: 'action',
                    header: 'Ação',
                    wrap: true,
                    render: (e) => (
                      <button
                        type="button"
                        className={styles.actionButton}
                        onClick={() => setSelected(e)}
                        aria-label={`Ver detalhes: ${e.action_label}`}
                      >
                        {e.is_denial ? (
                          <Badge tone="danger" withDot>
                            {e.action_label}
                          </Badge>
                        ) : (
                          <span className={styles.actionLabel}>{e.action_label}</span>
                        )}
                        {e.reason_label && <small>{e.reason_label}</small>}
                      </button>
                    ),
                  },
                  {
                    key: 'entity',
                    header: 'Afetado',
                    wrap: true,
                    render: (e) => e.entity_label ?? '—',
                  },
                ]}
              />
              <div className={styles.pagination}>
                <Button
                  variant="secondary"
                  icon={<ChevronLeft size={16} />}
                  disabled={!page.previous}
                  onClick={() => setQuery((q) => ({ ...q, page: q.page - 1 }))}
                >
                  Anterior
                </Button>
                <Button
                  variant="secondary"
                  icon={<ChevronRight size={16} />}
                  disabled={!page.next}
                  onClick={() => setQuery((q) => ({ ...q, page: q.page + 1 }))}
                >
                  Próxima
                </Button>
              </div>
            </>
          )}
        </Card>
        {selected && <AuditEventDetails event={selected} onClose={() => setSelected(null)} />}
      </div>
    </>
  );
}

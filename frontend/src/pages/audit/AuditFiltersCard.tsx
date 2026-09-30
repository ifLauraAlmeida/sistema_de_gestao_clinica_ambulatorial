import { useState, type FormEvent, type ReactElement } from 'react';
import { Search } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { SelectField } from '../../components/ui/SelectField';
import { TextField } from '../../components/ui/TextField';
import type { AuditQuery, AuditSummary } from '../../types/audit';
import styles from './AuditPage.module.css';

interface AuditFiltersCardProps {
  query: AuditQuery;
  summary: AuditSummary | null;
  onChange: (query: AuditQuery) => void;
}

const OUTCOME_OPTIONS = [
  { value: 'denied', label: 'Somente negados' },
  { value: 'granted', label: 'Somente concedidos' },
];

/** Filtros: período, usuário, categoria, resultado e paciente/senha. */
export function AuditFiltersCard({
  query,
  summary,
  onChange,
}: AuditFiltersCardProps): ReactElement {
  const [search, setSearch] = useState(query.search ?? '');
  const update = (changes: Partial<AuditQuery>): void =>
    onChange({ ...query, ...changes, page: 1 });

  function submitSearch(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault();
    update({ search: search.trim() || undefined });
  }

  return (
    <Card>
      <form className={styles.filters} onSubmit={submitSearch} role="search">
        <TextField
          label="De"
          type="date"
          value={query.date_from}
          onChange={(e) => e.target.value && update({ date_from: e.target.value })}
        />
        <TextField
          label="Até"
          type="date"
          value={query.date_to}
          onChange={(e) => e.target.value && update({ date_to: e.target.value })}
        />
        <SelectField
          label="Usuário"
          placeholder="Todos"
          value={query.user ?? ''}
          options={(summary?.users ?? []).map((u) => ({
            value: u.id,
            label: `${u.display_name} (${u.role_label})`,
          }))}
          onChange={(e) => update({ user: e.target.value || undefined })}
        />
        <SelectField
          label="Categoria"
          placeholder="Todas"
          value={query.category ?? ''}
          options={summary?.categories ?? []}
          onChange={(e) => update({ category: e.target.value || undefined })}
        />
        <SelectField
          label="Resultado"
          placeholder="Todos"
          value={query.outcome ?? ''}
          options={OUTCOME_OPTIONS}
          onChange={(e) =>
            update({ outcome: (e.target.value || undefined) as AuditQuery['outcome'] })
          }
        />
        <div className={styles.searchField}>
          <TextField
            label="Paciente ou senha"
            placeholder="Ex.: Maria, RX01"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <Button type="submit" variant="secondary" icon={<Search size={16} />}>
            Buscar
          </Button>
        </div>
      </form>
    </Card>
  );
}

import { useState, type ReactElement } from 'react';
import { Search } from 'lucide-react';
import { Badge, type BadgeTone } from '../../components/ui/Badge';
import { EmptyState } from '../../components/ui/EmptyState';
import { Loading } from '../../components/ui/Loading';
import { Table } from '../../components/ui/Table';
import { TextField } from '../../components/ui/TextField';
import { useApiResource } from '../../hooks/useApiResource';
import { getCatalogTree } from '../../services/catalog';
import type { CatalogService, ServiceType } from '../../types/catalog';
import { countServices, filterCatalog } from './catalogFilter';
import styles from './CatalogPage.module.css';

const TYPE_TONES: Record<ServiceType, BadgeTone> = {
  CONSULTA: 'info',
  SESSAO: 'success',
  PROCEDIMENTO: 'warning',
  EXAME: 'neutral',
};

function attributesOf(service: CatalogService): string {
  const attributes = [];
  if (service.requires_laterality) attributes.push('lateralidade');
  if (service.allows_sedation) attributes.push('sedação opcional');
  if (service.is_laboratory_collection) attributes.push('exames laboratoriais');
  if (service.has_execution_form) attributes.push('campos de registro');
  return attributes.join(', ') || '—';
}

/** Áreas recolhíveis → grupos → serviços, com busca por nome ou sinônimo. */
export function ServicesTab(): ReactElement {
  const tree = useApiResource(getCatalogTree);
  const [search, setSearch] = useState('');
  const filtered = filterCatalog(tree.data ?? [], search);

  if (tree.isLoading) return <Loading />;

  return (
    <div className={styles.tab}>
      <TextField
        label="Buscar serviço"
        placeholder="Nome ou sinônimo (ex.: ergometria, mapeamento cerebral)"
        icon={<Search size={18} />}
        value={search}
        onChange={(event) => setSearch(event.target.value)}
      />
      <p className={styles.count}>{countServices(filtered)} serviço(s)</p>
      {filtered.length === 0 && <EmptyState title="Nenhum serviço encontrado" />}
      {filtered.map((category) => (
        <details key={category.id} className={styles.area} open={Boolean(search.trim())}>
          <summary>
            {category.name}
            <span className={styles.count}>{countServices([category])} serviço(s)</span>
          </summary>
          {category.groups.map((group) => (
            <section key={group.id} className={styles.group} aria-label={group.name}>
              <h3>{group.name}</h3>
              <Table
                caption={`${category.name} — ${group.name}`}
                rows={group.services}
                getRowKey={(service) => service.id}
                columns={[
                  { key: 'name', header: 'Serviço', render: (s) => s.name },
                  {
                    key: 'type',
                    header: 'Tipo',
                    render: (s) => (
                      <Badge tone={TYPE_TONES[s.service_type]}>{s.service_type_label}</Badge>
                    ),
                  },
                  {
                    key: 'duration',
                    header: 'Duração',
                    render: (s) => `${s.duration_minutes} min`,
                  },
                  { key: 'attributes', header: 'Atributos', render: attributesOf },
                  {
                    key: 'aliases',
                    header: 'Sinônimos',
                    render: (s) => s.aliases.join(', ') || '—',
                  },
                ]}
              />
              {group.services
                .filter((service) => service.preparation_instructions)
                .map((service) => (
                  <p key={service.id} className={styles.preparation}>
                    <strong>{service.name}:</strong> {service.preparation_instructions}
                  </p>
                ))}
            </section>
          ))}
        </details>
      ))}
    </div>
  );
}

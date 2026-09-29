import type { ReactElement } from 'react';
import { Package } from 'lucide-react';
import { Card } from '../../components/ui/Card';
import { EmptyState } from '../../components/ui/EmptyState';
import { Loading } from '../../components/ui/Loading';
import { useApiResource } from '../../hooks/useApiResource';
import { listServicePackages } from '../../services/catalog';
import grid from '../../layouts/PageGrid.module.css';
import styles from './CatalogPage.module.css';

/** Pacotes (check-ups): composição de serviços e exames, mantida pelo gestor. */
export function PackagesTab(): ReactElement {
  const packages = useApiResource(listServicePackages);
  if (packages.isLoading) return <Loading />;
  if (!packages.data?.length) return <EmptyState title="Nenhum pacote cadastrado" />;

  return (
    <div className={grid.pair}>
      {packages.data.map((servicePackage) => (
        <Card key={servicePackage.id} title={servicePackage.name} icon={<Package size={20} />}>
          <p className={styles.count}>{servicePackage.description}</p>
          <ul className={styles.packageItems}>
            {servicePackage.items.map((item) => (
              <li key={item.id}>
                {item.name}
                <span className={styles.count}>
                  {item.kind === 'SERVICE' ? ' — serviço' : ' — exame laboratorial'}
                </span>
              </li>
            ))}
          </ul>
        </Card>
      ))}
    </div>
  );
}

import { useState, type ReactElement } from 'react';
import { Card } from '../../components/ui/Card';
import { PageHeader } from '../../components/ui/PageHeader';
import { LaboratoryExamsTab } from './LaboratoryExamsTab';
import { PackagesTab } from './PackagesTab';
import { ServicesTab } from './ServicesTab';
import styles from './CatalogPage.module.css';

const TABS = [
  { id: 'services', label: 'Serviços', render: () => <ServicesTab /> },
  { id: 'laboratory', label: 'Exames laboratoriais', render: () => <LaboratoryExamsTab /> },
  { id: 'packages', label: 'Pacotes', render: () => <PackagesTab /> },
] as const;

type TabId = (typeof TABS)[number]['id'];

/**
 * Consulta do catálogo: consultas, sessões, procedimentos e exames organizados
 * por área e grupo. Tempos, preços e preparo são mantidos pelo gestor no /admin.
 */
export function CatalogPage(): ReactElement {
  const [activeTab, setActiveTab] = useState<TabId>('services');
  const current = TABS.find((tab) => tab.id === activeTab) ?? TABS[0];

  return (
    <>
      <PageHeader
        title="Catálogo de serviços"
        subtitle="Consultas, sessões, procedimentos, exames e pacotes oferecidos pela clínica."
      />
      <Card>
        <div className={styles.tabs} role="tablist" aria-label="Seções do catálogo">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              type="button"
              role="tab"
              aria-selected={tab.id === activeTab}
              className={`${styles.tabButton} ${tab.id === activeTab ? styles.active : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>
        <div role="tabpanel">{current.render()}</div>
      </Card>
    </>
  );
}

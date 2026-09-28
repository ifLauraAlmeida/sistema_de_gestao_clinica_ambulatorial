import type { ReactElement } from 'react';
import { Construction } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { EmptyState } from '../components/ui/EmptyState';
import { PageHeader } from '../components/ui/PageHeader';

interface ModulePlaceholderPageProps {
  title: string;
  description: string;
}

/** Tela reservada para módulos previstos nas próximas etapas. */
export function ModulePlaceholderPage({
  title,
  description,
}: ModulePlaceholderPageProps): ReactElement {
  return (
    <>
      <PageHeader title={title} subtitle={description} />
      <Card>
        <EmptyState
          icon={<Construction size={24} />}
          title="Módulo em construção"
          description="Esta tela será disponibilizada nas próximas etapas do sistema."
        />
      </Card>
    </>
  );
}

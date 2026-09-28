import type { ReactElement } from 'react';
import { Link } from 'react-router-dom';
import { SearchX } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { EmptyState } from '../components/ui/EmptyState';

export function NotFoundPage(): ReactElement {
  return (
    <Card>
      <EmptyState icon={<SearchX size={24} />} title="Página não encontrada" />
      <Link to="/dashboard">Voltar ao dashboard</Link>
    </Card>
  );
}

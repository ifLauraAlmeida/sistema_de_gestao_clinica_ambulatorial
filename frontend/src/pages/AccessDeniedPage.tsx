import type { ReactElement } from 'react';
import { ShieldAlert } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { EmptyState } from '../components/ui/EmptyState';

export function AccessDeniedPage(): ReactElement {
  return (
    <Card>
      <EmptyState
        icon={<ShieldAlert size={24} />}
        title="Acesso não permitido"
        description="Seu perfil não tem permissão para esta tela. Em caso de dúvida, procure a gestão."
      />
    </Card>
  );
}

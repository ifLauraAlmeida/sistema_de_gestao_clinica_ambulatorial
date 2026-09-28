import type { ReactElement } from 'react';
import { History } from 'lucide-react';
import { Card } from '../ui/Card';
import { EmptyState } from '../ui/EmptyState';
import { Table } from '../ui/Table';
import type { QueueCall } from '../../types/queue';
import { formatTime } from '../../utils/dateTime';
import styles from './Queue.module.css';

export function RecentCallsCard({ calls }: { calls: QueueCall[] }): ReactElement {
  return (
    <Card title="Últimas chamadas" icon={<History size={20} />}>
      <Table
        caption="Últimas chamadas"
        rows={calls}
        getRowKey={(call) => call.id}
        emptyState={<EmptyState title="Nenhuma chamada hoje" />}
        columns={[
          { key: 'time', header: 'Horário', render: (call) => formatTime(call.called_at) },
          {
            key: 'ticket',
            header: 'Senha',
            render: (call) => <span className={styles.ticket}>{call.ticket_code}</span>,
          },
          { key: 'patient', header: 'Paciente', render: (call) => call.patient_name },
          { key: 'destination', header: 'Destino', render: (call) => call.destination_label },
          { key: 'attempt', header: 'Tentativa', render: (call) => `${call.attempt_number}ª` },
        ]}
      />
    </Card>
  );
}

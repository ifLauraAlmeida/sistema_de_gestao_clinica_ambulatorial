import type { ReactElement, ReactNode } from 'react';
import { AlertCircle, CheckCircle2, Info } from 'lucide-react';
import styles from './Alert.module.css';

type AlertTone = 'error' | 'success' | 'info';

const ICONS: Record<AlertTone, ReactNode> = {
  error: <AlertCircle size={18} />,
  success: <CheckCircle2 size={18} />,
  info: <Info size={18} />,
};

interface AlertProps {
  tone?: AlertTone;
  children: ReactNode;
}

/** Mensagem de feedback. Erros são anunciados imediatamente a leitores de tela. */
export function Alert({ tone = 'info', children }: AlertProps): ReactElement {
  return (
    <div className={`${styles.alert} ${styles[tone]}`} role={tone === 'error' ? 'alert' : 'status'}>
      {ICONS[tone]}
      <span>{children}</span>
    </div>
  );
}

import type { ReactElement } from 'react';
import { CalendarDays } from 'lucide-react';
import { formatLongDate } from '../../utils/dateTime';
import styles from './Dashboard.module.css';

export function TodayBadge({ now }: { now: Date }): ReactElement {
  return (
    <div className={styles.today}>
      <CalendarDays size={20} aria-hidden="true" />
      <span>{formatLongDate(now)}</span>
    </div>
  );
}

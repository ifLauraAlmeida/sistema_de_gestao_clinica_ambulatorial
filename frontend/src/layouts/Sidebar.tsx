import type { ReactElement } from 'react';
import { NavLink } from 'react-router-dom';
import { Activity } from 'lucide-react';
import { getVisibleNavigationItems } from '../app/navigation';
import { useCurrentUser } from '../hooks/useAuth';
import styles from './Sidebar.module.css';

export function Sidebar(): ReactElement {
  const user = useCurrentUser();

  return (
    <aside className={styles.sidebar}>
      <div className={styles.brand}>
        <span className={styles.brandIcon} aria-hidden="true">
          <Activity size={22} />
        </span>
        <span className={styles.brandName}>Sistema de Gestão Clínica Ambulatorial</span>
      </div>
      <nav aria-label="Menu principal">
        <ul className={styles.menu}>
          {getVisibleNavigationItems(user).map(({ path, label, icon: Icon }) => (
            <li key={path}>
              <NavLink
                to={path}
                className={({ isActive }) => `${styles.link} ${isActive ? styles.active : ''}`}
              >
                <Icon size={20} aria-hidden="true" />
                {label}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
}

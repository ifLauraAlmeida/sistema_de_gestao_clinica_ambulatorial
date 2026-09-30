import type { ReactElement } from 'react';
import { NavLink } from 'react-router-dom';
import { Activity } from 'lucide-react';
import { getVisibleNavigationItems } from '../app/navigation';
import { useCurrentUser } from '../hooks/useAuth';
import styles from './Sidebar.module.css';

export const SIDEBAR_ID = 'menu-lateral';

/**
 * Menu lateral. Recolhido, desliza para fora da tela e fica inerte: não recebe
 * foco pelo teclado nem é lido por leitores de tela.
 */
export function Sidebar({ isOpen }: { isOpen: boolean }): ReactElement {
  const user = useCurrentUser();

  return (
    <aside
      id={SIDEBAR_ID}
      className={`${styles.sidebar} ${isOpen ? '' : styles.closed}`}
      aria-hidden={!isOpen}
      inert={!isOpen}
    >
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

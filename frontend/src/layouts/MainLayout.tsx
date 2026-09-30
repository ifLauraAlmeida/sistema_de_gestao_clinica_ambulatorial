import type { ReactElement } from 'react';
import { Outlet } from 'react-router-dom';
import { useSidebarPreference } from '../hooks/useSidebarPreference';
import { Sidebar, SIDEBAR_ID } from './Sidebar';
import { Topbar } from './Topbar';
import styles from './MainLayout.module.css';

/** Estrutura das telas internas: menu lateral recolhível, topbar e conteúdo. */
export function MainLayout(): ReactElement {
  const sidebar = useSidebarPreference();

  return (
    <div className={styles.shell}>
      <Sidebar isOpen={sidebar.isOpen} />
      <div className={styles.main}>
        <Topbar
          isSidebarOpen={sidebar.isOpen}
          sidebarId={SIDEBAR_ID}
          onToggleSidebar={sidebar.toggle}
        />
        <main className={styles.content}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}

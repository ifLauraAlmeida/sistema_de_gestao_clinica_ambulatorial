import { useState, type ReactElement } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { DoorOpen, LogOut } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { useAuth, useCurrentUser } from '../hooks/useAuth';
import { initialsOf } from '../utils/userAccess';
import styles from './Topbar.module.css';

export function Topbar(): ReactElement {
  const user = useCurrentUser();
  const { signOut } = useAuth();
  const navigate = useNavigate();
  const [isSigningOut, setSigningOut] = useState(false);
  const station = user.active_work_session?.station;

  async function handleSignOut(): Promise<void> {
    setSigningOut(true);
    await signOut().catch(() => undefined);
    navigate('/login', { replace: true });
  }

  return (
    <header className={styles.topbar} aria-label="Barra superior">
      <div className={styles.station}>
        <DoorOpen size={18} aria-hidden="true" />
        <span>
          {station ? (
            <>
              Posto atual: <strong>{station.name}</strong>
            </>
          ) : (
            'Sem posto de trabalho'
          )}
        </span>
        <Link to="/workstation" className={styles.changeStation}>
          {station ? 'Trocar' : 'Selecionar'}
        </Link>
      </div>
      <div className={styles.user}>
        <span className={styles.avatar} aria-hidden="true">
          {initialsOf(user)}
        </span>
        <div className={styles.identity}>
          <span className={styles.name}>{user.display_name}</span>
          <span className={styles.role}>{user.role_label}</span>
        </div>
        <Button
          variant="ghost"
          icon={<LogOut size={18} />}
          onClick={handleSignOut}
          isLoading={isSigningOut}
        >
          Sair
        </Button>
      </div>
    </header>
  );
}

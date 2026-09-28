import { useState, type ReactElement } from 'react';
import { useNavigate } from 'react-router-dom';
import { DoorOpen, LogOut, MonitorSmartphone } from 'lucide-react';
import { Alert } from '../../components/ui/Alert';
import { Button } from '../../components/ui/Button';
import { EmptyState } from '../../components/ui/EmptyState';
import { Loading } from '../../components/ui/Loading';
import { useApiResource } from '../../hooks/useApiResource';
import { useAuth, useCurrentUser } from '../../hooks/useAuth';
import { listAvailableStations, startWorkSession } from '../../services/workSession';
import type { Station, StationType } from '../../types/workSession';
import { describeError } from '../../utils/errorMessages';
import styles from './WorkstationPage.module.css';

const INSTRUCTIONS: Record<StationType | 'ANY', string> = {
  RECEPTION_DESK: 'Informe em qual guichê você está atendendo antes de chamar pacientes.',
  CONSULTATION_ROOM: 'Informe em qual consultório você está atendendo antes de chamar pacientes.',
  ANY: 'Selecione um posto apenas se for realizar chamadas.',
};

/** Seleção do guichê/consultório que inicia a sessão de trabalho. */
export function WorkstationPage(): ReactElement {
  const user = useCurrentUser();
  const { refreshUser, signOut } = useAuth();
  const navigate = useNavigate();
  const stations = useApiResource(listAvailableStations);
  const [selectingId, setSelectingId] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function selectStation(station: Station): Promise<void> {
    setSelectingId(station.id);
    setErrorMessage(null);
    try {
      await startWorkSession(station.id);
      await refreshUser();
      navigate('/dashboard', { replace: true });
    } catch (error) {
      setErrorMessage(describeError(error, 'Não foi possível iniciar a sessão de trabalho.'));
      setSelectingId(null);
    }
  }

  async function handleSignOut(): Promise<void> {
    await signOut().catch(() => undefined);
    navigate('/login', { replace: true });
  }

  const currentStationId = user.active_work_session?.station.id;

  return (
    <div className={styles.page}>
      <main className={styles.panel}>
        <header className={styles.header}>
          <h1>Olá, {user.display_name}!</h1>
          <p>{INSTRUCTIONS[user.required_station_type ?? 'ANY']}</p>
        </header>
        {errorMessage && <Alert tone="error">{errorMessage}</Alert>}
        {stations.isLoading && <Loading label="Carregando postos…" />}
        {Boolean(stations.error) && (
          <Alert tone="error">Não foi possível carregar os postos de trabalho.</Alert>
        )}
        {stations.data?.length === 0 && (
          <EmptyState
            icon={<MonitorSmartphone size={24} />}
            title="Nenhum posto disponível"
            description="Peça à gestão para cadastrar guichês ou consultórios."
          />
        )}
        <ul className={styles.grid} aria-label="Postos de trabalho">
          {stations.data?.map((station) => (
            <li key={station.id}>
              <button
                type="button"
                className={`${styles.station} ${station.id === currentStationId ? styles.current : ''}`}
                onClick={() => void selectStation(station)}
                disabled={selectingId !== null}
                aria-busy={selectingId === station.id}
              >
                <DoorOpen size={28} aria-hidden="true" />
                <span className={styles.stationName}>{station.name}</span>
                <span className={styles.stationType}>{station.station_type_label}</span>
              </button>
            </li>
          ))}
        </ul>
        <footer className={styles.footer}>
          {user.required_station_type === null && (
            <Button variant="secondary" onClick={() => navigate('/dashboard')}>
              Continuar sem posto
            </Button>
          )}
          <Button variant="ghost" icon={<LogOut size={18} />} onClick={handleSignOut}>
            Sair
          </Button>
        </footer>
      </main>
    </div>
  );
}

import type { Station, WorkSession } from '../types/workSession';
import { apiClient } from './api';

/** Guichês ou consultórios que o perfil do usuário pode ocupar. */
export function listAvailableStations(): Promise<Station[]> {
  return apiClient.get<Station[]>('/work-sessions/stations/');
}

export function startWorkSession(stationId: string): Promise<WorkSession> {
  return apiClient.post<WorkSession>('/work-sessions/', { station_id: stationId });
}

export async function endWorkSession(): Promise<void> {
  await apiClient.post<undefined>('/work-sessions/current/end/');
}

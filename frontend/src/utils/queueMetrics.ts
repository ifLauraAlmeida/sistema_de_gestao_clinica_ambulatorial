import type { BadgeTone } from '../components/ui/Badge';
import type { QueueEntry } from '../types/queue';

/** Espera a partir da qual o paciente é destacado em vermelho (Tela 06). */
export const LONG_WAIT_MINUTES = 30;
const MODERATE_WAIT_MINUTES = 15;

export interface QueueSummary {
  waiting: number;
  called: number;
  averageWaitMinutes: number;
  longWaitCount: number;
}

/** Minutos desde a entrada na fila. */
export function waitingMinutes(entry: QueueEntry, now: Date): number {
  const elapsed = now.getTime() - new Date(entry.entered_at).getTime();
  return Math.max(0, Math.floor(elapsed / 60_000));
}

/** Cor do tempo de espera: verde, âmbar ou vermelho. */
export function waitTone(minutes: number): BadgeTone {
  if (minutes >= LONG_WAIT_MINUTES) return 'danger';
  if (minutes >= MODERATE_WAIT_MINUTES) return 'warning';
  return 'success';
}

/**
 * Indicadores de exibição calculados a partir da fila já autorizada pelo backend.
 *
 * Exemplo:
 *   summarizeQueue(entries, new Date()).averageWaitMinutes
 */
export function summarizeQueue(entries: QueueEntry[], now: Date): QueueSummary {
  const minutes = entries.map((entry) => waitingMinutes(entry, now));
  const total = minutes.reduce((sum, value) => sum + value, 0);
  return {
    waiting: entries.filter((entry) => entry.status === 'WAITING').length,
    called: entries.filter((entry) => entry.status === 'CALLED').length,
    averageWaitMinutes: entries.length ? Math.round(total / entries.length) : 0,
    longWaitCount: minutes.filter((value) => value >= LONG_WAIT_MINUTES).length,
  };
}

/** Próxima senha aguardando, na ordem de chegada. */
export function nextWaitingEntry(entries: QueueEntry[]): QueueEntry | undefined {
  return entries.find((entry) => entry.status === 'WAITING');
}

/**
 * Senha selecionada para chamada: a escolhida pelo usuário, se ainda estiver na
 * fila; caso contrário, a próxima aguardando.
 */
export function resolveSelectedEntry(
  entries: QueueEntry[],
  selectedId: string | null,
): QueueEntry | undefined {
  return entries.find((entry) => entry.id === selectedId) ?? nextWaitingEntry(entries);
}

/** Paciente chamado pode ter o atendimento iniciado (o backend também valida). */
export function canStartEncounter(entry: QueueEntry): boolean {
  return entry.encounter_status === 'CHAMADO';
}

/** Atendimento chamado ou em andamento pode ser finalizado (o backend também valida). */
export function canCompleteEncounter(entry: QueueEntry): boolean {
  return entry.encounter_status === 'CHAMADO' || entry.encounter_status === 'EM_ATENDIMENTO';
}

/**
 * Falta só pode ser registrada para senha já chamada e paciente ainda fora do
 * consultório (o backend aplica a mesma regra).
 */
export function canMarkNoShow(entry: QueueEntry): boolean {
  return entry.status === 'CALLED' && entry.encounter_status !== 'EM_ATENDIMENTO';
}

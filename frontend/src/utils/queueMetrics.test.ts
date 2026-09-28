import { describe, expect, it } from 'vitest';
import type { QueueEntry } from '../types/queue';
import { nextWaitingEntry, summarizeQueue, waitTone, waitingMinutes } from './queueMetrics';

const NOW = new Date('2026-09-28T13:00:00Z');

function entry(id: string, minutesAgo: number, status: QueueEntry['status']): QueueEntry {
  return {
    id,
    encounter_id: `enc-${id}`,
    queue_type: 'RECEPTION',
    ticket_code: `GINE0${id}`,
    patient_name: 'Paciente Fictício',
    specialty_name: 'Ginecologia',
    professional_name: 'Profissional Fictício',
    status,
    status_label: '',
    encounter_status: 'CHECK_IN_REALIZADO',
    encounter_status_label: '',
    entered_at: new Date(NOW.getTime() - minutesAgo * 60_000).toISOString(),
    finished_at: null,
    last_call_destination: null,
    last_called_at: null,
    last_call_attempt: null,
  };
}

describe('queueMetrics', () => {
  it('calcula minutos de espera', () => {
    expect(waitingMinutes(entry('1', 12, 'WAITING'), NOW)).toBe(12);
  });

  it('classifica a espera em verde, âmbar e vermelho', () => {
    expect(waitTone(5)).toBe('success');
    expect(waitTone(20)).toBe('warning');
    expect(waitTone(30)).toBe('danger');
  });

  it('resume a fila', () => {
    const entries = [entry('1', 40, 'CALLED'), entry('2', 10, 'WAITING'), entry('3', 4, 'WAITING')];

    expect(summarizeQueue(entries, NOW)).toEqual({
      waiting: 2,
      called: 1,
      averageWaitMinutes: 18,
      longWaitCount: 1,
    });
    expect(nextWaitingEntry(entries)?.id).toBe('2');
  });

  it('resume fila vazia sem dividir por zero', () => {
    expect(summarizeQueue([], NOW).averageWaitMinutes).toBe(0);
  });
});

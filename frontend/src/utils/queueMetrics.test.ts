import { describe, expect, it } from 'vitest';
import { buildQueueEntry } from '../test/domainFixtures';
import type { QueueEntry } from '../types/queue';
import {
  nextWaitingEntry,
  resolveSelectedEntry,
  summarizeQueue,
  waitTone,
  waitingMinutes,
} from './queueMetrics';

const NOW = new Date('2026-09-28T13:00:00Z');

function entry(id: string, minutesAgo: number, status: QueueEntry['status']): QueueEntry {
  const enteredAt = new Date(NOW.getTime() - minutesAgo * 60_000).toISOString();
  return buildQueueEntry({ id, status, entered_at: enteredAt });
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

  it('usa a senha escolhida e volta para a próxima quando ela sai da fila', () => {
    const entries = [entry('1', 10, 'WAITING'), entry('2', 5, 'WAITING')];

    expect(resolveSelectedEntry(entries, '2')?.id).toBe('2');
    expect(resolveSelectedEntry(entries, 'removida')?.id).toBe('1');
  });
});

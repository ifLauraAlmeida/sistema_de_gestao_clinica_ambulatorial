import { describe, expect, it } from 'vitest';
import { buildUser } from '../test/userFixtures';
import { getVisibleNavigationItems } from './navigation';

function labelsFor(role: Parameters<typeof buildUser>[0]): string[] {
  return getVisibleNavigationItems(buildUser(role)).map((item) => item.label);
}

describe('menu por permissões', () => {
  it('atendente vê somente módulos administrativos da recepção', () => {
    expect(labelsFor('ATENDENTE')).toEqual([
      'Dashboard',
      'Pacientes',
      'Agenda',
      'Check-in',
      'Fila da recepção',
    ]);
  });

  it('médico vê somente a fila clínica', () => {
    expect(labelsFor('MEDICO')).toEqual(['Dashboard', 'Fila clínica']);
  });

  it('gestor vê auditoria', () => {
    expect(labelsFor('GESTOR')).toContain('Auditoria');
  });
});

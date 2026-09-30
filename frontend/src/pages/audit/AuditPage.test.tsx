import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { FakeBackend } from '../../test/FakeBackend';
import { renderApp } from '../../test/renderApp';
import { buildUser } from '../../test/userFixtures';
import type { AuditEvent } from '../../types/audit';

const deniedEvent: AuditEvent = {
  id: 'ev1',
  timestamp: '2026-09-29T16:36:41Z',
  action: 'MEDICAL_RECORD_VIEW_DENIED',
  action_label: 'Prontuário negado',
  category: 'CLINICAL',
  category_label: 'Prontuário e procedimentos',
  is_denial: true,
  reason_label: 'atendimento de outro profissional',
  user: { id: 'u1', username: 'carla', display_name: 'Carla Médica', role_label: 'Médico' },
  entity_type: 'encounter',
  entity_id: 'enc-1',
  entity_label: 'GINE01 · Consulta · Paciente Um',
  ip_address: '10.0.0.7',
  metadata: {
    reason: 'encounter_of_another_professional',
    patient_id: 'p1',
    operation: 'view_medical_record',
  },
};

function auditBackend(): FakeBackend {
  return new FakeBackend()
    .on('GET', '/api/v1/auth/me/', () => ({ status: 200, body: buildUser('GESTOR') }))
    .on('GET', '/api/v1/audit/summary/', () => ({
      status: 200,
      body: {
        today: { total: 12, denied: 1, medical_records_opened: 4, failed_logins: 0 },
        categories: [{ value: 'CLINICAL', label: 'Prontuário e procedimentos' }],
        users: [{ id: 'u1', display_name: 'Carla Médica', role_label: 'Médico' }],
      },
    }))
    .on('GET', '/api/v1/audit/events/', () => ({
      status: 200,
      body: { count: 1, next: null, previous: null, results: [deniedEvent] },
    }));
}

describe('AuditPage', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('lista eventos com negação destacada e abre os detalhes', async () => {
    auditBackend().install();
    renderApp('/auditoria');

    expect(await screen.findByText('Prontuário negado')).toBeInTheDocument();
    expect(screen.getByText('atendimento de outro profissional')).toBeInTheDocument();
    expect(screen.getByText('GINE01 · Consulta · Paciente Um')).toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: 'Ver detalhes: Prontuário negado' }));

    expect(screen.getByText('Detalhes do evento')).toBeInTheDocument();
    expect(screen.getByText('10.0.0.7')).toBeInTheDocument();
    expect(screen.queryByText('p1')).toBeNull();
  });

  it('aplica filtros na consulta e no link de exportação', async () => {
    const backend = auditBackend();
    backend.install();
    renderApp('/auditoria');

    await screen.findByText('Prontuário negado');
    await userEvent.selectOptions(screen.getByLabelText('Resultado'), 'denied');
    await userEvent.type(screen.getByLabelText('Paciente ou senha'), 'GINE01{Enter}');

    const eventRequests = (): string[] =>
      backend.requests
        .map((request) => request.path)
        .filter((path) => path.startsWith('/api/v1/audit/events/?'));
    await waitFor(() => expect(eventRequests().at(-1)).toContain('search=GINE01'));
    expect(eventRequests().at(-1)).toContain('outcome=denied');
    expect(screen.getByRole('link', { name: /Exportar CSV/ })).toHaveAttribute(
      'href',
      expect.stringContaining('/api/v1/audit/events/export/?'),
    );
  });
});

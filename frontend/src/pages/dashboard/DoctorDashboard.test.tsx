import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { FakeBackend } from '../../test/FakeBackend';
import { buildQueueEntry } from '../../test/domainFixtures';
import { renderApp } from '../../test/renderApp';
import { buildUser, buildWorkSession } from '../../test/userFixtures';

describe('DoctorDashboard', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('médico escolhe qual senha chamar, não apenas a próxima', async () => {
    const doctor = buildUser('MEDICO', buildWorkSession('Consultório 03', 'CONSULTATION_ROOM'));
    const first = buildQueueEntry({ id: 'e1', ticket_code: 'GINE01', patient_name: 'Paciente Um' });
    const second = buildQueueEntry({
      id: 'e2',
      ticket_code: 'GINE02',
      patient_name: 'Paciente Dois',
    });
    const backend = new FakeBackend()
      .on('GET', '/api/v1/auth/me/', () => ({ status: 200, body: doctor }))
      .on('GET', '/api/v1/clinical-queue/?status=active', () => ({
        status: 200,
        body: [first, second],
      }))
      .on('GET', '/api/v1/clinical-queue/?status=inactive', () => ({ status: 200, body: [] }))
      .on('POST', '/api/v1/auth/csrf/', () => ({ status: 204 }))
      .on('POST', '/api/v1/clinical-queue/e2/call/', () => ({
        status: 201,
        body: { ticket_code: 'GINE02', destination_label: 'Consultório 03' },
      }));
    backend.install();
    renderApp('/dashboard');

    await userEvent.selectOptions(await screen.findByLabelText('Senha a chamar'), 'e2');
    await userEvent.click(screen.getByRole('button', { name: 'Chamar senha selecionada' }));

    await waitFor(() =>
      expect(backend.requestsTo('POST', '/api/v1/clinical-queue/e2/call/')).toHaveLength(1),
    );
    expect(backend.requestsTo('POST', '/api/v1/clinical-queue/e1/call/')).toHaveLength(0);
    expect(
      await screen.findByText('Senha GINE02 chamada para Consultório 03.'),
    ).toBeInTheDocument();
  });
});

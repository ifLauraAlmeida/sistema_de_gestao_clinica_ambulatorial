import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { FakeBackend } from '../../test/FakeBackend';
import { buildQueueEntry } from '../../test/domainFixtures';
import { renderApp } from '../../test/renderApp';
import { buildUser, buildWorkSession } from '../../test/userFixtures';
import type { CurrentUser } from '../../types/auth';
import type { QueueEntry } from '../../types/queue';

const doctor = buildUser('MEDICO', buildWorkSession('Consultório 03', 'CONSULTATION_ROOM'));

function clinicalBackend(user: CurrentUser, active: QueueEntry[]): FakeBackend {
  return new FakeBackend()
    .on('GET', '/api/v1/auth/me/', () => ({ status: 200, body: user }))
    .on('GET', '/api/v1/clinical-queue/?status=active', () => ({ status: 200, body: active }))
    .on('GET', '/api/v1/clinical-queue/?status=inactive', () => ({ status: 200, body: [] }))
    .on('GET', '/api/v1/professionals/', () => ({
      status: 200,
      body: [{ id: 'prof-2', name: 'Médica Fictícia', specialties: [] }],
    }));
}

describe('ClinicalQueuePage', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('médico escolhe qual senha chamar, não apenas a próxima', async () => {
    const first = buildQueueEntry({ id: 'e1', ticket_code: 'GINE01', patient_name: 'Paciente Um' });
    const second = buildQueueEntry({
      id: 'e2',
      ticket_code: 'GINE02',
      patient_name: 'Paciente Dois',
    });
    const backend = clinicalBackend(doctor, [first, second]).on(
      'POST',
      '/api/v1/clinical-queue/e2/call/',
      () => ({ status: 201, body: { ticket_code: 'GINE02', destination_label: 'Consultório 03' } }),
    );
    backend.install();
    renderApp('/fila-clinica');

    await userEvent.selectOptions(await screen.findByLabelText('Senha a chamar'), 'e2');
    await userEvent.click(screen.getByRole('button', { name: 'Chamar senha selecionada' }));

    expect(
      await screen.findByText('Senha GINE02 chamada para Consultório 03.'),
    ).toBeInTheDocument();
    expect(backend.requestsTo('POST', '/api/v1/clinical-queue/e1/call/')).toHaveLength(0);
  });

  it('médico inicia o atendimento do paciente chamado e acessa o prontuário', async () => {
    const called = buildQueueEntry({
      id: 'e1',
      encounter_id: 'enc-1',
      status: 'CALLED',
      encounter_status: 'CHAMADO',
    });
    const backend = clinicalBackend(doctor, [called]).on(
      'POST',
      '/api/v1/encounters/enc-1/start/',
      () => ({ status: 200, body: {} }),
    );
    backend.install();
    renderApp('/fila-clinica');

    expect(await screen.findByRole('link', { name: 'Abrir atendimento' })).toHaveAttribute(
      'href',
      '/atendimento/enc-1',
    );
    await userEvent.click(screen.getByRole('button', { name: 'Iniciar atendimento' }));

    await waitFor(() =>
      expect(backend.requestsTo('POST', '/api/v1/encounters/enc-1/start/')).toHaveLength(1),
    );
  });

  it('gestor filtra as filas por profissional, sem ações de chamada', async () => {
    const backend = clinicalBackend(buildUser('GESTOR'), [buildQueueEntry()]);
    backend.install();
    renderApp('/fila-clinica');

    await screen.findByRole('option', { name: 'Médica Fictícia' });
    await userEvent.selectOptions(screen.getByLabelText('Profissional'), 'prof-2');

    await waitFor(() =>
      expect(
        backend.requestsTo('GET', '/api/v1/clinical-queue/?status=active&professional_id=prof-2'),
      ).toHaveLength(1),
    );
    expect(screen.queryByRole('button', { name: /Chamar/ })).toBeNull();
  });

  it('paciente em atendimento aparece como em atendimento, sem botão de chamar', async () => {
    const inProgress = buildQueueEntry({
      status: 'CALLED',
      status_label: 'Chamado',
      encounter_status: 'EM_ATENDIMENTO',
      encounter_status_label: 'Em atendimento',
    });
    clinicalBackend(doctor, [inProgress]).install();
    renderApp('/fila-clinica');

    expect(await screen.findByText('Em atendimento')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Rechamar' })).toBeNull();
  });
});

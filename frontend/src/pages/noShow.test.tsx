import { fireEvent, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { FakeBackend } from '../test/FakeBackend';
import { buildQueueEntry } from '../test/domainFixtures';
import { renderApp } from '../test/renderApp';
import { buildUser, buildWorkSession } from '../test/userFixtures';

// Math.random() = 0 sorteia sempre a primeira palavra da lista.
const WORD = 'AUSENTE';

const calledEntry = buildQueueEntry({
  id: 'e1',
  ticket_code: 'GINE01',
  patient_name: 'Paciente Um',
  status: 'CALLED',
  status_label: 'Chamado',
  encounter_status: 'CHAMADO',
  last_call_attempt: 2,
});

function doctorBackend(): FakeBackend {
  const doctor = buildUser('MEDICO', buildWorkSession('Consultório 03', 'CONSULTATION_ROOM'));
  return new FakeBackend()
    .on('GET', '/api/v1/auth/me/', () => ({ status: 200, body: doctor }))
    .on('GET', '/api/v1/clinical-queue/?status=active', () => ({
      status: 200,
      body: [calledEntry],
    }))
    .on('GET', '/api/v1/clinical-queue/?status=inactive', () => ({ status: 200, body: [] }))
    .on('POST', '/api/v1/clinical-queue/e1/no-show/', () => ({ status: 200, body: {} }));
}

describe('não comparecimento', () => {
  beforeEach(() => vi.spyOn(Math, 'random').mockReturnValue(0));
  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it('médico só registra a falta após digitar a palavra sorteada', async () => {
    const backend = doctorBackend();
    backend.install();
    renderApp('/fila-clinica');

    await userEvent.click(await screen.findByRole('button', { name: 'Não compareceu' }));
    const dialog = screen.getByRole('alertdialog', { name: 'Registrar não comparecimento?' });
    expect(within(dialog).getByText(/irrevogável/)).toBeInTheDocument();
    expect(within(dialog).getByText(/chamada 2 vezes/)).toBeInTheDocument();
    const confirm = within(dialog).getByRole('button', { name: 'Registrar falta' });
    const input = within(dialog).getByLabelText(`Digite ${WORD} para confirmar`);

    await userEvent.type(input, 'ausente');
    expect(confirm).toBeDisabled();
    await userEvent.clear(input);
    await userEvent.type(input, WORD);
    expect(confirm).toBeEnabled();
    await userEvent.click(confirm);

    await waitFor(() =>
      expect(backend.requestsTo('POST', '/api/v1/clinical-queue/e1/no-show/')).toHaveLength(1),
    );
    expect(
      await screen.findByText('Não comparecimento registrado para a senha GINE01.'),
    ).toBeInTheDocument();
    expect(screen.queryByRole('alertdialog')).toBeNull();
  });

  it('cancelar ou colar a palavra não registra a falta', async () => {
    const backend = doctorBackend();
    backend.install();
    renderApp('/fila-clinica');

    await userEvent.click(await screen.findByRole('button', { name: 'Não compareceu' }));
    const input = screen.getByLabelText(`Digite ${WORD} para confirmar`);
    fireEvent.paste(input, { clipboardData: { getData: () => WORD } });
    expect(screen.getByRole('button', { name: 'Registrar falta' })).toBeDisabled();
    await userEvent.click(screen.getByRole('button', { name: 'Cancelar' }));

    expect(screen.queryByRole('alertdialog')).toBeNull();
    expect(backend.requestsTo('POST', '/api/v1/clinical-queue/e1/no-show/')).toHaveLength(0);
  });

  it('senha ainda não chamada não oferece o registro de falta', async () => {
    const doctor = buildUser('MEDICO', buildWorkSession('Consultório 03', 'CONSULTATION_ROOM'));
    new FakeBackend()
      .on('GET', '/api/v1/auth/me/', () => ({ status: 200, body: doctor }))
      .on('GET', '/api/v1/clinical-queue/?status=active', () => ({
        status: 200,
        body: [buildQueueEntry({ status: 'WAITING' })],
      }))
      .on('GET', '/api/v1/clinical-queue/?status=inactive', () => ({ status: 200, body: [] }))
      .install();
    renderApp('/fila-clinica');

    expect(await screen.findByRole('button', { name: 'Chamar' })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Não compareceu' })).toBeNull();
  });

  it('recepção registra falta com a mesma confirmação', async () => {
    const attendant = buildUser('ATENDENTE', buildWorkSession('Guichê 02', 'RECEPTION_DESK'));
    const receptionEntry = { ...calledEntry, id: 'r1', queue_type: 'RECEPTION' as const };
    const backend = new FakeBackend()
      .on('GET', '/api/v1/auth/me/', () => ({ status: 200, body: attendant }))
      .on('GET', '/api/v1/reception-queue/', () => ({ status: 200, body: [receptionEntry] }))
      .on('GET', '/api/v1/reception-queue/calls/', () => ({ status: 200, body: [] }))
      .on('POST', '/api/v1/reception-queue/r1/no-show/', () => ({ status: 200, body: {} }));
    backend.install();
    renderApp('/fila-recepcao');

    await userEvent.click(await screen.findByRole('button', { name: 'Não compareceu' }));
    await userEvent.type(screen.getByLabelText(`Digite ${WORD} para confirmar`), WORD);
    await userEvent.click(screen.getByRole('button', { name: 'Registrar falta' }));

    await waitFor(() =>
      expect(backend.requestsTo('POST', '/api/v1/reception-queue/r1/no-show/')).toHaveLength(1),
    );
  });
});

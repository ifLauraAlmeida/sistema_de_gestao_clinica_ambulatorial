import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { FakeBackend } from '../../test/FakeBackend';
import { renderApp } from '../../test/renderApp';
import { buildUser, buildWorkSession } from '../../test/userFixtures';
import type { MedicalRecord } from '../../types/medicalRecord';

const doctor = buildUser('MEDICO', buildWorkSession('Consultório 03', 'CONSULTATION_ROOM'));
const RECORD_URL = '/api/v1/encounters/enc-1/medical-record/';

function buildRecord(status: 'CHAMADO' | 'EM_ATENDIMENTO' = 'EM_ATENDIMENTO'): MedicalRecord {
  return {
    encounter: {
      id: 'enc-1',
      ticket_code: 'GINE01',
      service_date: '2026-09-28',
      patient_name: 'Paciente Fictício Alfa',
      professional_name: 'Beatriz Gineco',
      specialty_name: 'Ginecologia',
      status,
      status_label: status === 'CHAMADO' ? 'Chamado' : 'Em atendimento',
      checked_in_at: '2026-09-28T11:00:00Z',
      completed_at: null,
    },
    patient: {
      id: 'p1',
      display_name: 'Paciente Fictício Alfa',
      full_name: 'Paciente Fictício Alfa',
      birth_date: '1985-03-12',
      age: 41,
    },
    clinical_notes: [],
  };
}

function encounterBackend(): FakeBackend {
  return new FakeBackend()
    .on('GET', '/api/v1/auth/me/', () => ({ status: 200, body: doctor }))
    .on('GET', RECORD_URL, () => ({ status: 200, body: buildRecord() }))
    .on('GET', '/api/v1/encounters/enc-1/clinical-history/', () => ({
      status: 200,
      body: [
        {
          id: 'old',
          service_date: '2025-01-10',
          specialty_name: 'Ginecologia',
          professional_name: 'Beatriz Gineco',
          clinical_notes: [
            { id: 'n0', content: 'Evolução anterior fictícia.', author_name: 'B', created_at: '' },
          ],
        },
      ],
    }))
    .on('GET', '/api/v1/clinical-queue/?status=active', () => ({ status: 200, body: [] }))
    .on('GET', '/api/v1/clinical-queue/?status=inactive', () => ({ status: 200, body: [] }));
}

describe('EncounterPage', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('mostra paciente e histórico clínico anterior', async () => {
    encounterBackend().install();
    renderApp('/atendimento/enc-1');

    expect(await screen.findByText('Paciente Fictício Alfa')).toBeInTheDocument();
    expect(screen.getByText('41 anos')).toBeInTheDocument();
    expect(await screen.findByText('Evolução anterior fictícia.')).toBeInTheDocument();
  });

  it('registra evolução clínica', async () => {
    const backend = encounterBackend().on(
      'POST',
      '/api/v1/encounters/enc-1/clinical-notes/',
      () => ({
        status: 201,
        body: { id: 'n1', content: 'Paciente estável.', author_name: 'B', created_at: '' },
      }),
    );
    backend.install();
    renderApp('/atendimento/enc-1');

    await userEvent.type(await screen.findByLabelText('Evolução clínica'), 'Paciente estável.');
    await userEvent.click(screen.getByRole('button', { name: 'Salvar evolução' }));

    await waitFor(() =>
      expect(
        backend.requestsTo('POST', '/api/v1/encounters/enc-1/clinical-notes/')[0]?.body,
      ).toEqual({
        content: 'Paciente estável.',
      }),
    );
  });

  it('finaliza somente após confirmação e volta para a fila', async () => {
    const backend = encounterBackend().on('POST', '/api/v1/encounters/enc-1/complete/', () => ({
      status: 200,
      body: {},
    }));
    backend.install();
    renderApp('/atendimento/enc-1');

    await userEvent.click(await screen.findByRole('button', { name: 'Finalizar atendimento' }));
    expect(backend.requestsTo('POST', '/api/v1/encounters/enc-1/complete/')).toHaveLength(0);
    await userEvent.click(screen.getByRole('button', { name: 'Confirmar finalização' }));

    expect(await screen.findByText('Atendimento finalizado.')).toBeInTheDocument();
    expect(backend.requestsTo('POST', '/api/v1/encounters/enc-1/complete/')).toHaveLength(1);
  });

  it('exibe a negação do backend sem dados clínicos', async () => {
    encounterBackend()
      .on('GET', RECORD_URL, () => ({
        status: 403,
        body: {
          error: {
            code: 'medical_record_access_denied',
            message: 'Acesso ao prontuário não autorizado para este atendimento.',
          },
        },
      }))
      .install();
    renderApp('/atendimento/enc-1');

    expect(await screen.findByText('Prontuário indisponível')).toBeInTheDocument();
    expect(
      screen.getByText('Acesso ao prontuário não autorizado para este atendimento.'),
    ).toBeInTheDocument();
    expect(screen.queryByLabelText('Evolução clínica')).toBeNull();
  });
});

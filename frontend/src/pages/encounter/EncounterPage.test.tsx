import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { FakeBackend } from '../../test/FakeBackend';
import { renderApp } from '../../test/renderApp';
import { buildUser, buildWorkSession } from '../../test/userFixtures';
import type { CurrentUser } from '../../types/auth';
import type { EncounterSummary, MedicalRecord } from '../../types/medicalRecord';
import type { ProcedureView } from '../../types/procedure';

const doctor = buildUser('MEDICO', buildWorkSession('Consultório 03', 'CONSULTATION_ROOM'));
const technician = buildUser('TECNICO', buildWorkSession('Sala de Raio-X', 'EXAM_ROOM'));
const BASE = '/api/v1/encounters/enc-1';

const encounter: EncounterSummary = {
  id: 'enc-1',
  ticket_code: 'RX01',
  service_date: '2026-09-29',
  patient_name: 'Paciente Fictício Alfa',
  professional_name: 'Rafael Radiologia',
  specialty_name: 'Radiologia',
  status: 'EM_ATENDIMENTO',
  status_label: 'Em atendimento',
  checked_in_at: '2026-09-29T11:00:00Z',
  completed_at: null,
  service_name: 'Raio-X de joelho',
  laterality_label: 'Direita',
  with_sedation: false,
};

const patient = {
  id: 'p1',
  display_name: 'Paciente Fictício Alfa',
  full_name: 'Paciente Fictício Alfa',
  birth_date: '1985-03-12',
  age: 41,
};

function buildProcedure(overrides: Partial<ProcedureView> = {}): ProcedureView {
  return {
    encounter,
    patient,
    service_type_label: 'Exame',
    preparation: '',
    laboratory_exams: [],
    form: {
      name: 'Radiografia',
      fields: [
        {
          key: 'incidencias',
          label: 'Incidências realizadas',
          field_type: 'TEXT',
          unit: '',
          options: [],
          is_required: true,
        },
        {
          key: 'exposicoes',
          label: 'Número de exposições',
          field_type: 'NUMBER',
          unit: '',
          options: [],
          is_required: false,
        },
      ],
    },
    values: null,
    recorded_at: null,
    recorded_by_name: null,
    can_edit: true,
    ...overrides,
  };
}

const record: MedicalRecord = { encounter, patient, clinical_notes: [] };

function encounterBackend(user: CurrentUser): FakeBackend {
  return new FakeBackend()
    .on('GET', '/api/v1/auth/me/', () => ({ status: 200, body: user }))
    .on('GET', `${BASE}/procedure/`, () => ({ status: 200, body: buildProcedure() }))
    .on('GET', `${BASE}/medical-record/`, () => ({ status: 200, body: record }))
    .on('GET', `${BASE}/clinical-history/`, () => ({
      status: 200,
      body: [
        {
          id: 'old',
          service_date: '2025-01-10',
          specialty_name: 'Ortopedia',
          professional_name: 'Carlos Orto',
          clinical_notes: [
            { id: 'n0', content: 'Evolução anterior fictícia.', author_name: 'C', created_at: '' },
          ],
        },
      ],
    }))
    .on('GET', '/api/v1/clinical-queue/?status=active', () => ({ status: 200, body: [] }))
    .on('GET', '/api/v1/clinical-queue/?status=inactive', () => ({ status: 200, body: [] }));
}

describe('EncounterPage', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('técnico vê o que realizar e registra o procedimento, sem prontuário', async () => {
    const backend = encounterBackend(technician).on('PUT', `${BASE}/procedure/`, (body) => ({
      status: 200,
      body: buildProcedure({
        values: (body as { values: ProcedureView['values'] }).values,
        recorded_at: '2026-09-29T12:00:00Z',
        recorded_by_name: 'Rafael Radiologia',
      }),
    }));
    backend.install();
    renderApp('/atendimento/enc-1');

    expect(await screen.findByText('Execução do atendimento')).toBeInTheDocument();
    expect(screen.getAllByText('Raio-X de joelho — Direita').length).toBeGreaterThan(0);
    await userEvent.type(screen.getByLabelText('Incidências realizadas *'), 'AP e perfil');
    await userEvent.type(screen.getByLabelText('Número de exposições'), '2');
    await userEvent.click(screen.getByRole('button', { name: 'Salvar registro' }));

    await waitFor(() =>
      expect(backend.requestsTo('PUT', `${BASE}/procedure/`)[0]?.body).toEqual({
        values: { incidencias: 'AP e perfil', exposicoes: 2 },
      }),
    );
    expect(backend.requestsTo('GET', `${BASE}/medical-record/`)).toHaveLength(0);
    expect(screen.queryByLabelText('Evolução clínica')).toBeNull();
  });

  it('médico vê procedimento, evolução e histórico clínico', async () => {
    encounterBackend(doctor).install();
    renderApp('/atendimento/enc-1');

    expect(await screen.findByText('Prontuário e atendimento')).toBeInTheDocument();
    expect(await screen.findByText('Evolução anterior fictícia.')).toBeInTheDocument();
    expect(screen.getByLabelText('Evolução clínica')).toBeInTheDocument();
    expect(screen.getByText('41 anos')).toBeInTheDocument();
  });

  it('exibe erros de validação por campo', async () => {
    encounterBackend(technician)
      .on('PUT', `${BASE}/procedure/`, () => ({
        status: 400,
        body: {
          error: {
            code: 'procedure_form_invalid',
            message: 'Há campos do procedimento com valores inválidos.',
            details: { incidencias: ['Campo obrigatório.'] },
          },
        },
      }))
      .install();
    renderApp('/atendimento/enc-1');

    await userEvent.click(await screen.findByRole('button', { name: 'Salvar registro' }));

    expect(await screen.findByText('Campo obrigatório.')).toBeInTheDocument();
  });

  it('finaliza somente após confirmação e volta para a fila', async () => {
    const backend = encounterBackend(doctor).on('POST', `${BASE}/complete/`, () => ({
      status: 200,
      body: {},
    }));
    backend.install();
    renderApp('/atendimento/enc-1');

    await userEvent.click(await screen.findByRole('button', { name: 'Finalizar atendimento' }));
    expect(backend.requestsTo('POST', `${BASE}/complete/`)).toHaveLength(0);
    await userEvent.click(screen.getByRole('button', { name: 'Confirmar finalização' }));

    expect(await screen.findByText('Atendimento finalizado.')).toBeInTheDocument();
  });

  it('exibe a negação do backend sem dados do paciente', async () => {
    encounterBackend(doctor)
      .on('GET', `${BASE}/procedure/`, () => ({
        status: 403,
        body: {
          error: {
            code: 'procedure_access_denied',
            message: 'Acesso ao procedimento não autorizado para este atendimento.',
          },
        },
      }))
      .install();
    renderApp('/atendimento/enc-1');

    expect(await screen.findByText('Atendimento indisponível')).toBeInTheDocument();
    expect(screen.queryByText('Paciente Fictício Alfa')).toBeNull();
  });
});

import { screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { FakeBackend } from '../test/FakeBackend';
import { buildAppointment, buildQueueEntry } from '../test/domainFixtures';
import { renderApp } from '../test/renderApp';
import { buildUser, buildWorkSession } from '../test/userFixtures';

const attendant = buildUser('ATENDENTE', buildWorkSession('Guichê 02', 'RECEPTION_DESK'));

function receptionBackend(): FakeBackend {
  return new FakeBackend()
    .on('GET', '/api/v1/auth/me/', () => ({ status: 200, body: attendant }))
    .on('GET', '/api/v1/reception-queue/', () => ({ status: 200, body: [] }))
    .on('GET', '/api/v1/reception-queue/calls/', () => ({ status: 200, body: [] }))
    .on('GET', '/api/v1/professionals/', () => ({ status: 200, body: [] }))
    .on('GET', '/api/v1/appointments/', () => ({ status: 200, body: [] }));
}

describe('páginas da recepção', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('cadastra paciente enviando CPF vazio como nulo', async () => {
    const backend = receptionBackend()
      .on('GET', '/api/v1/patients/', () => ({
        status: 200,
        body: { count: 0, next: null, previous: null, results: [] },
      }))
      .on('POST', '/api/v1/patients/', (body) => ({
        status: 201,
        body: { ...(body as object), id: 'p1', is_active: true },
      }));
    backend.install();
    renderApp('/pacientes');

    await userEvent.click(await screen.findByRole('button', { name: 'Novo paciente' }));
    await userEvent.type(screen.getByLabelText('Nome completo *'), 'Paciente Novo');
    await userEvent.type(screen.getByLabelText('Data de nascimento *'), '1990-05-01');
    await userEvent.click(screen.getByRole('button', { name: 'Salvar cadastro' }));

    expect(await screen.findByText('Cadastro de Paciente Novo criado.')).toBeInTheDocument();
    expect(backend.requestsTo('POST', '/api/v1/patients/')[0]?.body).toMatchObject({
      full_name: 'Paciente Novo',
      birth_date: '1990-05-01',
      cpf: null,
    });
  });

  it('exibe erro de validação do CPF no campo', async () => {
    receptionBackend()
      .on('GET', '/api/v1/patients/', () => ({
        status: 200,
        body: { count: 0, next: null, previous: null, results: [] },
      }))
      .on('POST', '/api/v1/patients/', () => ({
        status: 400,
        body: {
          error: {
            code: 'validation_error',
            message: 'Dados inválidos.',
            details: { cpf: ['CPF inválido.'] },
          },
        },
      }))
      .install();
    renderApp('/pacientes');

    await userEvent.click(await screen.findByRole('button', { name: 'Novo paciente' }));
    await userEvent.type(screen.getByLabelText('CPF'), '111');
    await userEvent.click(screen.getByRole('button', { name: 'Salvar cadastro' }));

    expect(await screen.findByText('CPF inválido.')).toBeInTheDocument();
    expect(screen.getByLabelText('CPF')).toHaveAttribute('aria-invalid', 'true');
  });

  it('confirma agendamento pela agenda', async () => {
    const backend = receptionBackend()
      .on('GET', '/api/v1/appointments/', () => ({ status: 200, body: [buildAppointment()] }))
      .on('PATCH', '/api/v1/appointments/appointment-1/', () => ({
        status: 200,
        body: buildAppointment({ status: 'CONFIRMADO', status_label: 'Confirmado' }),
      }));
    backend.install();
    renderApp('/agenda');

    await userEvent.click(
      await screen.findByRole('button', { name: 'Ver detalhes de Paciente Fictício Alfa' }),
    );
    expect(screen.getByRole('link', { name: 'Ligar para (00) 90000-0001' })).toHaveAttribute(
      'href',
      'tel:00900000001',
    );
    await userEvent.click(screen.getByRole('button', { name: 'Confirmar' }));

    await waitFor(() =>
      expect(backend.requestsTo('PATCH', '/api/v1/appointments/appointment-1/')[0]?.body).toEqual({
        status: 'CONFIRMADO',
      }),
    );
  });

  it('registra chegada e mostra a senha gerada', async () => {
    const backend = receptionBackend()
      .on('GET', '/api/v1/appointments/', () => ({ status: 200, body: [buildAppointment()] }))
      .on('POST', '/api/v1/check-ins/', () => ({
        status: 201,
        body: {
          id: 'enc-1',
          ticket_code: 'GINE03',
          patient_name: 'Paciente Fictício Alfa',
          specialty_name: 'Ginecologia',
          professional_name: 'Profissional Fictício',
          status_label: 'Check-in realizado',
        },
      }));
    backend.install();
    renderApp('/check-in');

    await userEvent.click(await screen.findByRole('button', { name: 'Confirmar chegada' }));

    const confirmation = await screen.findByText(/Chegada registrada/);
    expect(
      within(confirmation.parentElement as HTMLElement).getByText('GINE03'),
    ).toBeInTheDocument();
    expect(backend.requestsTo('POST', '/api/v1/check-ins/')[0]?.body).toEqual({
      appointment_id: 'appointment-1',
    });
  });

  it('atendente escolhe a senha e chama para o próprio guichê', async () => {
    const entries = [
      buildQueueEntry({ id: 'r1', queue_type: 'RECEPTION', ticket_code: 'ORTO01' }),
      buildQueueEntry({ id: 'r2', queue_type: 'RECEPTION', ticket_code: 'GINE04' }),
    ];
    const backend = receptionBackend()
      .on('GET', '/api/v1/reception-queue/', () => ({ status: 200, body: entries }))
      .on('POST', '/api/v1/reception-queue/r2/call/', () => ({
        status: 201,
        body: { ticket_code: 'GINE04', destination_label: 'Guichê 02' },
      }));
    backend.install();
    renderApp('/fila-recepcao');

    await userEvent.selectOptions(await screen.findByLabelText('Senha a chamar'), 'r2');
    await userEvent.click(screen.getByRole('button', { name: 'Chamar senha selecionada' }));

    expect(await screen.findByText('Senha GINE04 chamada para Guichê 02.')).toBeInTheDocument();
  });

  it('agenda serviço exigindo lateralidade e filtra profissionais pela especialidade', async () => {
    const service = {
      id: 'svc-joelho',
      name: 'Raio-X de joelho',
      service_type: 'EXAME',
      service_type_label: 'Exame',
      duration_minutes: 15,
      requires_laterality: true,
      allows_sedation: false,
      is_laboratory_collection: false,
      preparation_instructions: '',
      specialty_id: 'rx',
      specialty_name: 'Radiologia',
      group_name: 'Membro inferior',
      category_name: 'Raios-X',
      aliases: [],
      has_execution_form: true,
    };
    const backend = receptionBackend()
      .on('GET', '/api/v1/professionals/', () => ({
        status: 200,
        body: [
          {
            id: 'tec',
            name: 'Rafael Radiologia',
            specialties: [{ id: 'rx', name: 'Radiologia', ticket_prefix: 'RX' }],
          },
          {
            id: 'orto',
            name: 'Carlos Orto',
            specialties: [{ id: 'o', name: 'Ortopedia', ticket_prefix: 'ORTO' }],
          },
        ],
      }))
      .on('GET', '/api/v1/patients/', () => ({
        status: 200,
        body: {
          count: 1,
          next: null,
          previous: null,
          results: [
            {
              id: 'p1',
              full_name: 'Paciente Um',
              social_name: '',
              cpf_masked: '',
              birth_date: '1990-01-01',
              phone: '',
              is_active: true,
            },
          ],
        },
      }))
      .on('GET', '/api/v1/catalog/services/', () => ({ status: 200, body: [service] }))
      .on('POST', '/api/v1/appointments/', () => ({
        status: 201,
        body: buildAppointment({ id: 'novo', patient_name: 'Paciente Um' }),
      }));
    backend.install();
    renderApp('/agenda');

    await userEvent.click(await screen.findByRole('button', { name: 'Novo agendamento' }));
    await userEvent.type(screen.getByLabelText('Localizar paciente'), 'um{Enter}');
    await userEvent.type(screen.getByLabelText('Buscar serviço'), 'joelho{Enter}');
    const professional = await screen.findByLabelText('Profissional *');
    expect(within(professional).queryByText('Carlos Orto')).toBeNull();
    await userEvent.selectOptions(screen.getByLabelText('Lateralidade *'), 'DIREITA');
    await userEvent.type(screen.getByLabelText('Horário *'), '10:30');
    await userEvent.click(screen.getByRole('button', { name: 'Agendar' }));

    await waitFor(() =>
      expect(backend.requestsTo('POST', '/api/v1/appointments/')[0]?.body).toMatchObject({
        patient: 'p1',
        professional: 'tec',
        service: 'svc-joelho',
        laterality: 'DIREITA',
        laboratory_exams: [],
      }),
    );
  });
});

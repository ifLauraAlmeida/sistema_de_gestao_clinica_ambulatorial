import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { FakeBackend } from '../../test/FakeBackend';
import { renderApp } from '../../test/renderApp';
import { buildUser, buildWorkSession } from '../../test/userFixtures';
import type { BillingDay, BillingEntry } from '../../types/billing';

const entry = (overrides: Partial<BillingEntry>): BillingEntry => ({
  encounter_id: 'e1',
  ticket_code: 'RX01',
  patient_name: 'Paciente Um',
  service_name: 'Raio-X de joelho',
  payer_label: '—',
  insurer_id: null,
  guide_number: '',
  payment_method: '',
  status: 'PENDENTE',
  status_label: 'Pendente',
  amount: '150.00',
  ...overrides,
});

const DAY: BillingDay = {
  date: '2026-09-29',
  today: { paid: 16, pending: 7, released: 22, received_amount: '8460.00' },
  previous_day: { paid: 13, pending: 5, released: 19, received_amount: '7550.00' },
  entries: [
    entry({ encounter_id: 'e1', patient_name: 'Paciente Um' }),
    entry({
      encounter_id: 'e2',
      patient_name: 'Paciente Dois',
      payer_label: 'Convênio Alfa Saúde',
      guide_number: '1234567',
      status: 'LIBERADO',
      status_label: 'Liberado',
    }),
  ],
};

function financeBackend(): FakeBackend {
  return new FakeBackend()
    .on('GET', '/api/v1/auth/me/', () => ({ status: 200, body: buildUser('GESTOR') }))
    .on('GET', '/api/v1/billing/day/', () => ({ status: 200, body: DAY }))
    .on('GET', '/api/v1/billing/insurers/', () => ({
      status: 200,
      body: [{ id: 'ins-1', name: 'Convênio Alfa Saúde' }],
    }));
}

describe('FinancePage', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('mostra indicadores com comparação a ontem e pacientes de hoje', async () => {
    financeBackend().install();
    renderApp('/financeiro');

    expect(await screen.findByText('Pacientes de hoje', { selector: 'h2' })).toBeInTheDocument();
    expect(screen.getByText('R$ 8.460,00')).toBeInTheDocument();
    expect(screen.getByText('+23%')).toBeInTheDocument();
    expect(screen.getByText('1234567')).toBeInTheDocument();
    expect(screen.getAllByText('Liberado').length).toBeGreaterThan(0);
  });

  it('confirma pagamento particular do paciente selecionado', async () => {
    const backend = financeBackend().on('POST', '/api/v1/billing/encounters/e1/payment/', () => ({
      status: 200,
      body: entry({ status: 'PAGO', status_label: 'Pago', payer_label: 'Particular' }),
    }));
    backend.install();
    renderApp('/financeiro');

    await userEvent.click(
      await screen.findByRole('button', {
        name: /Registrar pagamento ou autorização de Paciente Um/,
      }),
    );
    await userEvent.selectOptions(screen.getByLabelText('Forma de pagamento'), 'PIX');
    await userEvent.click(screen.getByRole('button', { name: 'Confirmar pagamento' }));

    await waitFor(() =>
      expect(backend.requestsTo('POST', '/api/v1/billing/encounters/e1/payment/')[0]?.body).toEqual(
        { insurer: null, guide_number: '', payment_method: 'PIX', amount: '150.00' },
      ),
    );
    expect(await screen.findByText('Pagamento confirmado: Paciente Um.')).toBeInTheDocument();
  });

  it('só libera atendimento com convênio e número da guia', async () => {
    const backend = financeBackend().on(
      'POST',
      '/api/v1/billing/encounters/e1/authorization/',
      () => ({ status: 200, body: entry({ status: 'LIBERADO', status_label: 'Liberado' }) }),
    );
    backend.install();
    renderApp('/financeiro');

    const release = await screen.findByRole('button', { name: 'Liberar atendimento' });
    expect(release).toBeDisabled();
    await userEvent.selectOptions(screen.getByLabelText('Convênio'), 'ins-1');
    await userEvent.type(screen.getByLabelText('Número da guia'), '9988776');
    await userEvent.click(release);

    await waitFor(() =>
      expect(
        backend.requestsTo('POST', '/api/v1/billing/encounters/e1/authorization/')[0]?.body,
      ).toEqual({ insurer: 'ins-1', guide_number: '9988776', amount: '150.00' }),
    );
  });

  it('atendente não acessa o financeiro', async () => {
    new FakeBackend()
      .on('GET', '/api/v1/auth/me/', () => ({
        status: 200,
        body: buildUser('ATENDENTE', buildWorkSession('Guichê 01', 'RECEPTION_DESK')),
      }))
      .install();
    renderApp('/financeiro');

    expect(await screen.findByText('Acesso não permitido')).toBeInTheDocument();
  });
});

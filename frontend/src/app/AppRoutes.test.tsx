import { screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { FakeBackend } from '../test/FakeBackend';
import { renderApp } from '../test/renderApp';
import { buildUser, buildWorkSession } from '../test/userFixtures';
import type { CurrentUser } from '../types/auth';
import type { Station } from '../types/workSession';

const ME = '/api/v1/auth/me/';

function backendFor(user: CurrentUser | null): FakeBackend {
  return new FakeBackend()
    .on('GET', ME, () =>
      user
        ? { status: 200, body: user }
        : { status: 401, body: { error: { code: 'x', message: '' } } },
    )
    .on('GET', '/api/v1/reception-queue/', () => ({ status: 200, body: [] }))
    .on('GET', '/api/v1/reception-queue/calls/', () => ({ status: 200, body: [] }))
    .on('GET', '/api/v1/clinical-queue/?status=active', () => ({ status: 200, body: [] }))
    .on('GET', '/api/v1/clinical-queue/?status=inactive', () => ({ status: 200, body: [] }))
    .on('GET', '/api/v1/appointments/', () => ({ status: 200, body: [] }));
}

function station(name: string, type: Station['station_type']): Station {
  return { id: `id-${name}`, name, station_type: type, station_type_label: '' };
}

describe('proteção de rotas e fluxo por perfil', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('usuário não autenticado é enviado ao login', async () => {
    backendFor(null).install();
    renderApp('/dashboard');

    expect(await screen.findByRole('heading', { name: 'Bem-vindo de volta!' })).toBeInTheDocument();
  });

  it('atendente sem guichê seleciona o posto e segue para o dashboard', async () => {
    let user = buildUser('ATENDENTE');
    const desk = station('Guichê 04', 'RECEPTION_DESK');
    const backend = backendFor(null)
      .on('GET', ME, () => ({ status: 200, body: user }))
      .on('GET', '/api/v1/work-sessions/stations/', () => ({ status: 200, body: [desk] }))
      .on('POST', '/api/v1/work-sessions/', () => {
        user = buildUser('ATENDENTE', buildWorkSession('Guichê 04', 'RECEPTION_DESK'));
        return { status: 201, body: user.active_work_session };
      });
    backend.install();
    renderApp('/dashboard');

    await userEvent.click(await screen.findByRole('button', { name: /Guichê 04/ }));

    expect(
      await screen.findByText('Fila de atendimento (agora)', { selector: 'h2' }),
    ).toBeInTheDocument();
    expect(backend.requestsTo('POST', '/api/v1/work-sessions/')[0]?.body).toEqual({
      station_id: 'id-Guichê 04',
    });
    expect(
      within(screen.getByLabelText('Barra superior')).getByText('Guichê 04'),
    ).toBeInTheDocument();
  });

  it('médico sem sala é levado à seleção de consultório', async () => {
    backendFor(buildUser('MEDICO'))
      .on('GET', '/api/v1/work-sessions/stations/', () => ({
        status: 200,
        body: [station('Consultório 03', 'CONSULTATION_ROOM')],
      }))
      .install();
    renderApp('/dashboard');

    expect(await screen.findByText(/em qual consultório você está atendendo/)).toBeInTheDocument();
    expect(await screen.findByRole('button', { name: /Consultório 03/ })).toBeInTheDocument();
  });

  it('gestor vai direto ao dashboard com visão geral e auditoria no menu', async () => {
    backendFor(buildUser('GESTOR')).install();
    renderApp('/dashboard');

    expect(await screen.findByText('Filas clínicas', { selector: 'h2' })).toBeInTheDocument();
    const menu = screen.getByRole('navigation', { name: 'Menu principal' });
    expect(within(menu).getByRole('link', { name: 'Auditoria' })).toBeInTheDocument();
  });

  it('atendente não vê controles clínicos nem itens restritos', async () => {
    const user = buildUser('ATENDENTE', buildWorkSession('Guichê 01', 'RECEPTION_DESK'));
    backendFor(user).install();
    renderApp('/dashboard');

    expect(
      await screen.findByText('Fila de atendimento (agora)', { selector: 'h2' }),
    ).toBeInTheDocument();
    expect(screen.queryByText('Minha fila ativa')).toBeNull();
    const menu = screen.getByRole('navigation', { name: 'Menu principal' });
    expect(within(menu).queryByRole('link', { name: 'Auditoria' })).toBeNull();
    expect(within(menu).queryByRole('link', { name: 'Fila clínica' })).toBeNull();
  });

  it('médico vê somente a própria fila', async () => {
    const user = buildUser('MEDICO', buildWorkSession('Consultório 03', 'CONSULTATION_ROOM'));
    backendFor(user).install();
    renderApp('/dashboard');

    expect(await screen.findByText('Minha fila ativa', { selector: 'h2' })).toBeInTheDocument();
    expect(screen.queryByText('Fila da recepção', { selector: 'h2' })).toBeNull();
  });

  it('rota sem permissão exibe acesso não permitido', async () => {
    const user = buildUser('ATENDENTE', buildWorkSession('Guichê 01', 'RECEPTION_DESK'));
    backendFor(user).install();
    renderApp('/auditoria');

    expect(await screen.findByText('Acesso não permitido')).toBeInTheDocument();
  });
});

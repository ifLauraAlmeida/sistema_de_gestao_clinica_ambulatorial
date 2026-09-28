import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { FakeBackend } from '../../test/FakeBackend';
import { renderApp } from '../../test/renderApp';
import { buildUser, buildWorkSession } from '../../test/userFixtures';

const ME = '/api/v1/auth/me/';
const LOGIN = '/api/v1/auth/login/';

function anonymousBackend(): FakeBackend {
  return new FakeBackend()
    .on('GET', ME, () => ({
      status: 401,
      body: { error: { code: 'not_authenticated', message: '' } },
    }))
    .on('GET', '/api/v1/auth/csrf/', () => ({ status: 204 }));
}

describe('LoginPage', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('identifica o sistema e associa rótulos aos campos', async () => {
    anonymousBackend().install();
    renderApp('/login');

    expect(await screen.findByText('Sistema de Gestão Clínica Ambulatorial')).toBeInTheDocument();
    expect(screen.getByLabelText('Usuário')).toBeInTheDocument();
    expect(screen.getByLabelText('Senha')).toHaveAttribute('type', 'password');
  });

  it('entra com teclado e segue para o dashboard', async () => {
    const gestor = buildUser('GESTOR');
    const backend = anonymousBackend().on('POST', LOGIN, () => ({ status: 200, body: gestor }));
    backend
      .on('GET', '/api/v1/reception-queue/', () => ({ status: 200, body: [] }))
      .on('GET', '/api/v1/clinical-queue/?status=active', () => ({ status: 200, body: [] }))
      .on('GET', '/api/v1/clinical-queue/?status=inactive', () => ({ status: 200, body: [] }));
    backend.install();
    renderApp('/login');

    await userEvent.type(await screen.findByLabelText('Usuário'), 'gestao.demo');
    await userEvent.type(screen.getByLabelText('Senha'), 'senha-correta{Enter}');

    expect(await screen.findByText('Olá, Ana!')).toBeInTheDocument();
    expect(backend.requestsTo('POST', LOGIN)[0]?.body).toEqual({
      username: 'gestao.demo',
      password: 'senha-correta',
    });
  });

  it('exibe erro de credenciais e limpa a senha', async () => {
    anonymousBackend()
      .on('POST', LOGIN, () => ({
        status: 401,
        body: { error: { code: 'invalid_credentials', message: 'Usuário ou senha inválidos.' } },
      }))
      .install();
    renderApp('/login');

    await userEvent.type(await screen.findByLabelText('Usuário'), 'alguem');
    await userEvent.type(screen.getByLabelText('Senha'), 'errada');
    await userEvent.click(screen.getByRole('button', { name: /entrar/i }));

    expect(await screen.findByRole('alert')).toHaveTextContent('Usuário ou senha inválidos.');
    expect(screen.getByLabelText('Senha')).toHaveValue('');
  });

  it('mostra estado de carregamento durante o envio', async () => {
    let resolveLogin: (value: Response) => void = () => undefined;
    anonymousBackend().install();
    const originalFetch = globalThis.fetch;
    vi.stubGlobal(
      'fetch',
      vi.fn((input: string, init?: RequestInit) =>
        input === LOGIN
          ? new Promise<Response>((resolve) => (resolveLogin = resolve))
          : originalFetch(input, init),
      ),
    );
    renderApp('/login');

    await userEvent.type(await screen.findByLabelText('Usuário'), 'recepcao.demo');
    await userEvent.type(screen.getByLabelText('Senha'), 'senha{Enter}');

    expect(await screen.findByRole('button', { name: /entrando/i })).toBeDisabled();
    const user = buildUser('ATENDENTE', buildWorkSession('Guichê 01', 'RECEPTION_DESK'));
    resolveLogin(new Response(JSON.stringify(user), { status: 200 }));
    await waitFor(() => expect(screen.queryByRole('button', { name: /entrando/i })).toBeNull());
  });
});

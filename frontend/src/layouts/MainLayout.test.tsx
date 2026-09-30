import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { FakeBackend } from '../test/FakeBackend';
import { renderApp } from '../test/renderApp';
import { buildUser } from '../test/userFixtures';

describe('menu lateral recolhível', () => {
  beforeEach(() => {
    window.localStorage.clear();
    new FakeBackend()
      .on('GET', '/api/v1/auth/me/', () => ({ status: 200, body: buildUser('GESTOR') }))
      .on('GET', '/api/v1/reception-queue/', () => ({ status: 200, body: [] }))
      .on('GET', '/api/v1/clinical-queue/', () => ({ status: 200, body: [] }))
      .install();
  });
  afterEach(() => vi.unstubAllGlobals());

  it('recolhe e reabre o menu, lembrando a preferência', async () => {
    renderApp('/dashboard');

    const toggle = await screen.findByRole('button', { name: 'Recolher menu' });
    expect(toggle).toHaveAttribute('aria-expanded', 'true');
    expect(screen.getByRole('navigation', { name: 'Menu principal' })).toBeInTheDocument();

    await userEvent.click(toggle);

    expect(screen.queryByRole('navigation', { name: 'Menu principal' })).toBeNull();
    expect(screen.getByRole('button', { name: 'Abrir menu' })).toHaveAttribute(
      'aria-expanded',
      'false',
    );
    expect(window.localStorage.getItem('sgca.sidebar-open')).toBe('false');

    await userEvent.click(screen.getByRole('button', { name: 'Abrir menu' }));

    expect(screen.getByRole('navigation', { name: 'Menu principal' })).toBeInTheDocument();
  });

  it('respeita a preferência salva ao abrir o sistema', async () => {
    window.localStorage.setItem('sgca.sidebar-open', 'false');
    renderApp('/dashboard');

    expect(await screen.findByRole('button', { name: 'Abrir menu' })).toBeInTheDocument();
    expect(screen.queryByRole('navigation', { name: 'Menu principal' })).toBeNull();
  });
});

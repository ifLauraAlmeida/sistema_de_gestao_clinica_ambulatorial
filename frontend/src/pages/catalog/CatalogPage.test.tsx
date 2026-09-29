import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { FakeBackend } from '../../test/FakeBackend';
import { renderApp } from '../../test/renderApp';
import { buildUser, buildWorkSession } from '../../test/userFixtures';

const attendant = buildUser('ATENDENTE', buildWorkSession('Guichê 01', 'RECEPTION_DESK'));

describe('CatalogPage', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('busca serviços por sinônimo e mostra exames laboratoriais', async () => {
    new FakeBackend()
      .on('GET', '/api/v1/auth/me/', () => ({ status: 200, body: attendant }))
      .on('GET', '/api/v1/catalog/', () => ({
        status: 200,
        body: [
          {
            id: 'card',
            name: 'Cardiologia',
            groups: [
              {
                id: 'erg',
                name: 'Ergometria',
                services: [
                  {
                    id: 's1',
                    name: 'Teste ergométrico',
                    service_type: 'EXAME',
                    service_type_label: 'Exame',
                    duration_minutes: 45,
                    requires_laterality: false,
                    allows_sedation: false,
                    is_laboratory_collection: false,
                    preparation_instructions: 'Tênis confortável.',
                    specialty_id: 'c',
                    specialty_name: 'Cardiologia',
                    group_name: 'Ergometria',
                    category_name: 'Cardiologia',
                    aliases: ['Ergometria'],
                    has_execution_form: true,
                  },
                ],
              },
            ],
          },
        ],
      }))
      .on('GET', '/api/v1/catalog/laboratory-exams/', () => ({
        status: 200,
        body: [
          {
            id: 'l1',
            name: 'Glicemia de jejum',
            group: 'Glicemia e metabolismo',
            sample_type: 'SANGUE',
            sample_type_label: 'Sangue',
            preparation: '',
            fasting_hours: 8,
          },
        ],
      }))
      .install();
    renderApp('/catalogo');

    await userEvent.type(await screen.findByLabelText('Buscar serviço'), 'ergometria');
    expect(screen.getByText('Teste ergométrico')).toBeInTheDocument();
    expect(screen.getByText('45 min')).toBeInTheDocument();

    await userEvent.click(screen.getByRole('tab', { name: 'Exames laboratoriais' }));
    const [groupSummary] = await screen.findAllByText('Glicemia e metabolismo');
    await userEvent.click(groupSummary as HTMLElement);
    expect(screen.getByText('8 h')).toBeInTheDocument();
  });
});

import { describe, expect, it } from 'vitest';
import type { CatalogCategory, CatalogService } from '../../types/catalog';
import { countServices, filterCatalog } from './catalogFilter';

const service = (name: string, aliases: string[] = []): CatalogService => ({
  id: name,
  name,
  service_type: 'EXAME',
  service_type_label: 'Exame',
  duration_minutes: 30,
  reference_price: null,
  requires_laterality: false,
  allows_sedation: false,
  is_laboratory_collection: false,
  preparation_instructions: '',
  specialty_id: 's',
  specialty_name: 'S',
  group_name: 'G',
  category_name: 'C',
  aliases,
  has_execution_form: false,
});

const TREE: CatalogCategory[] = [
  {
    id: 'card',
    name: 'Cardiologia',
    groups: [
      { id: 'erg', name: 'Ergometria', services: [service('Teste ergométrico', ['Ergometria'])] },
    ],
  },
  {
    id: 'rx',
    name: 'Raios-X',
    groups: [{ id: 'mi', name: 'Membro inferior', services: [service('Raio-X de joelho')] }],
  },
];

describe('filterCatalog', () => {
  it('encontra por sinônimo e remove áreas vazias', () => {
    const result = filterCatalog(TREE, 'ergometria');

    expect(result.map((category) => category.name)).toEqual(['Cardiologia']);
    expect(countServices(result)).toBe(1);
  });

  it('ignora acentos', () => {
    expect(countServices(filterCatalog(TREE, 'ergometrico'))).toBe(1);
  });

  it('sem busca devolve tudo', () => {
    expect(countServices(filterCatalog(TREE, ''))).toBe(2);
  });
});

import type { CatalogCategory, CatalogService } from '../../types/catalog';

function normalize(text: string): string {
  return text.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
}

function matches(service: CatalogService, term: string): boolean {
  return [service.name, ...service.aliases].some((name) => normalize(name).includes(term));
}

/**
 * Filtra a árvore do catálogo por nome ou sinônimo (sem acentos), removendo
 * grupos e áreas que ficarem vazios.
 *
 * Exemplo:
 *   filterCatalog(tree, 'ergometria') // área Cardiologia → grupo Ergometria → Teste ergométrico
 */
export function filterCatalog(tree: CatalogCategory[], search: string): CatalogCategory[] {
  const term = normalize(search.trim());
  if (!term) return tree;
  return tree
    .map((category) => ({
      ...category,
      groups: category.groups
        .map((group) => ({ ...group, services: group.services.filter((s) => matches(s, term)) }))
        .filter((group) => group.services.length > 0),
    }))
    .filter((category) => category.groups.length > 0);
}

export function countServices(tree: CatalogCategory[]): number {
  return tree.reduce(
    (total, category) =>
      total + category.groups.reduce((sum, group) => sum + group.services.length, 0),
    0,
  );
}

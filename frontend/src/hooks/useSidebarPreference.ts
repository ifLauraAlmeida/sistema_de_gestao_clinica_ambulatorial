import { useCallback, useState } from 'react';

const STORAGE_KEY = 'sgca.sidebar-open';
// Telas estreitas começam com o menu recolhido para liberar espaço às tabelas.
const NARROW_SCREEN_QUERY = '(max-width: 1100px)';

function readInitialPreference(): boolean {
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored !== null) return stored === 'true';
  } catch {
    // Armazenamento indisponível (modo privado, bloqueio): usa o padrão.
  }
  return !window.matchMedia?.(NARROW_SCREEN_QUERY).matches;
}

/**
 * Menu lateral aberto/recolhido, lembrado por navegador.
 *
 * Guarda apenas preferência de exibição (nenhum dado do usuário ou paciente).
 */
export function useSidebarPreference(): { isOpen: boolean; toggle: () => void } {
  const [isOpen, setOpen] = useState(readInitialPreference);

  const toggle = useCallback(() => {
    setOpen((current) => {
      const next = !current;
      try {
        window.localStorage.setItem(STORAGE_KEY, String(next));
      } catch {
        // Sem persistência: a preferência vale só nesta aba.
      }
      return next;
    });
  }, []);

  return { isOpen, toggle };
}

import { useCallback, useEffect, useState } from 'react';

interface ApiResource<T> {
  data: T | null;
  error: unknown;
  isLoading: boolean;
  reload: () => Promise<void>;
}

interface ApiResourceOptions {
  /**
   * Intervalo de atualização automática, em milissegundos.
   *
   * Solução provisória para as filas até a publicação de eventos por WebSocket
   * (Django Channels), prevista para o módulo de chamadas em tempo real.
   */
  refreshIntervalMs?: number;
}

interface ResourceState<T> {
  data: T | null;
  error: unknown;
  isLoading: boolean;
}

/**
 * Carrega um recurso da API e expõe estado de carregamento, erro e recarga.
 *
 * `loader` deve ser estável (função de `services/` ou memoizada com useCallback).
 *
 * Exemplo:
 *   const { data, reload } = useApiResource(listReceptionQueue, { refreshIntervalMs: 15000 });
 */
export function useApiResource<T>(
  loader: () => Promise<T>,
  { refreshIntervalMs }: ApiResourceOptions = {},
): ApiResource<T> {
  const [state, setState] = useState<ResourceState<T>>({
    data: null,
    error: null,
    isLoading: true,
  });

  const reload = useCallback(
    (): Promise<void> =>
      loader().then(
        (data) => setState({ data, error: null, isLoading: false }),
        (error: unknown) => setState((previous) => ({ ...previous, error, isLoading: false })),
      ),
    [loader],
  );

  useEffect(() => {
    let isActive = true;
    const load = (): void => {
      loader().then(
        (data) => isActive && setState({ data, error: null, isLoading: false }),
        (error: unknown) =>
          isActive && setState((previous) => ({ ...previous, error, isLoading: false })),
      );
    };
    load();
    const timer = refreshIntervalMs ? window.setInterval(load, refreshIntervalMs) : undefined;
    return () => {
      isActive = false;
      window.clearInterval(timer);
    };
  }, [loader, refreshIntervalMs]);

  return { ...state, reload };
}

/**
 * Palavras usadas para confirmar ações irreversíveis. Sem acentos, para não
 * depender do layout do teclado.
 */
export const CONFIRMATION_WORDS = [
  'AUSENTE',
  'CADEIRA',
  'CANETA',
  'JANELA',
  'LANTERNA',
  'MOCHILA',
  'PRANCHETA',
  'RELOGIO',
  'SEMAFORO',
  'TAPETE',
  'TECLADO',
  'VARANDA',
] as const;

/**
 * Sorteia a palavra que o usuário precisa digitar para confirmar.
 *
 * Exemplo:
 *   pickConfirmationWord(() => 0) // "AUSENTE"
 */
export function pickConfirmationWord(random: () => number = Math.random): string {
  const index = Math.floor(random() * CONFIRMATION_WORDS.length);
  return CONFIRMATION_WORDS[index] ?? CONFIRMATION_WORDS[0];
}

/** A confirmação exige a palavra exata (maiúsculas), ignorando espaços nas pontas. */
export function isConfirmationWordTyped(typed: string, expected: string): boolean {
  return typed.trim() === expected;
}

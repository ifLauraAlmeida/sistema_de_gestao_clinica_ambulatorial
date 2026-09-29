import { describe, expect, it } from 'vitest';
import {
  CONFIRMATION_WORDS,
  isConfirmationWordTyped,
  pickConfirmationWord,
} from './confirmationWord';

describe('confirmationWord', () => {
  it('sorteia palavras da lista', () => {
    expect(pickConfirmationWord(() => 0)).toBe(CONFIRMATION_WORDS[0]);
    expect(pickConfirmationWord(() => 0.9999)).toBe(CONFIRMATION_WORDS.at(-1));
  });

  it('exige a palavra exata em maiúsculas', () => {
    expect(isConfirmationWordTyped(' JANELA ', 'JANELA')).toBe(true);
    expect(isConfirmationWordTyped('janela', 'JANELA')).toBe(false);
    expect(isConfirmationWordTyped('JANEL', 'JANELA')).toBe(false);
  });
});

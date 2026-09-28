const timeFormatter = new Intl.DateTimeFormat('pt-BR', { hour: '2-digit', minute: '2-digit' });
const longDateFormatter = new Intl.DateTimeFormat('pt-BR', {
  weekday: 'long',
  day: 'numeric',
  month: 'long',
  year: 'numeric',
});

/** "14:32" */
export function formatTime(isoDateTime: string): string {
  return timeFormatter.format(new Date(isoDateTime));
}

/** "Segunda-feira, 28 de setembro de 2026" */
export function formatLongDate(date: Date): string {
  const text = longDateFormatter.format(date);
  return text.charAt(0).toUpperCase() + text.slice(1);
}

const shortDateFormatter = new Intl.DateTimeFormat('pt-BR', { timeZone: 'UTC' });

/** "1985-03-12" → "12/03/1985" (datas sem horário, sem conversão de fuso). */
export function formatIsoDate(isoDate: string): string {
  return shortDateFormatter.format(new Date(`${isoDate}T00:00:00Z`));
}

/** Data local no formato aceito por `<input type="date">` e pela API: "2026-09-28". */
export function toIsoDate(date: Date): string {
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${date.getFullYear()}-${month}-${day}`;
}

/** Combina data ("2026-09-28") e hora ("14:30") locais em ISO 8601 com fuso. */
export function combineLocalDateTime(isoDate: string, time: string): string {
  return new Date(`${isoDate}T${time}:00`).toISOString();
}

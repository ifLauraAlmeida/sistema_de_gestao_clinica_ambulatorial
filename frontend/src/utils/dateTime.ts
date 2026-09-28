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

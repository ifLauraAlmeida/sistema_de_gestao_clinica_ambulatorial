import type { ReactElement } from 'react';
import { CalendarDays, Clock, FileText, Stethoscope } from 'lucide-react';
import styles from './LoginPage.module.css';

const HIGHLIGHTS = [
  {
    icon: <Clock size={24} />,
    tone: styles.highlightBlue,
    title: 'Filas em tempo real',
    description: 'Acompanhe a recepção e os consultórios sem fichas de papel.',
  },
  {
    icon: <FileText size={24} />,
    tone: styles.highlightGreen,
    title: 'Prontuário eletrônico',
    description: 'Histórico clínico acessível somente a quem está atendendo.',
  },
  {
    icon: <CalendarDays size={24} />,
    tone: styles.highlightRed,
    title: 'Agenda e recepção',
    description: 'Consultas, check-in e chamadas em poucos cliques.',
  },
];

/** Painel ilustrativo da tela de login (sem imagens nem marcas de terceiros). */
export function LoginHighlights(): ReactElement {
  return (
    <aside className={styles.highlightsColumn} aria-label="Recursos do sistema">
      <div className={styles.emblem} aria-hidden="true">
        <Stethoscope size={56} />
      </div>
      <ul className={styles.highlights}>
        {HIGHLIGHTS.map((highlight) => (
          <li key={highlight.title} className={styles.highlight}>
            <span className={`${styles.highlightIcon} ${highlight.tone}`} aria-hidden="true">
              {highlight.icon}
            </span>
            <div>
              <p className={styles.highlightTitle}>{highlight.title}</p>
              <p className={styles.highlightDescription}>{highlight.description}</p>
            </div>
          </li>
        ))}
      </ul>
    </aside>
  );
}

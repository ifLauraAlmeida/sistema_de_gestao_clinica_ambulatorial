import type { ReactElement } from 'react';
import { CalendarDays, Clock, FileText } from 'lucide-react';
// Ilustração genérica de recepção (sem marca), otimizada a partir de
// references/imagensdeapoio/.
import receptionIllustration from '../../assets/login-reception-illustration.webp';
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
      <img
        src={receptionIllustration}
        alt=""
        className={styles.illustration}
        width={1000}
        height={750}
      />
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

import type { ReactElement, ReactNode } from 'react';
import styles from './Table.module.css';

export interface TableColumn<Row> {
  key: string;
  header: string;
  render: (row: Row, index: number) => ReactNode;
  align?: 'left' | 'right';
  /** Permite quebra de linha (textos longos); por padrão as células não quebram. */
  wrap?: boolean;
}

interface TableProps<Row> {
  caption: string;
  columns: TableColumn<Row>[];
  rows: Row[];
  getRowKey: (row: Row) => string;
  emptyState?: ReactNode;
}

/** Tabela operacional compacta; `caption` fica disponível para leitores de tela. */
export function Table<Row>({
  caption,
  columns,
  rows,
  getRowKey,
  emptyState,
}: TableProps<Row>): ReactElement {
  if (rows.length === 0 && emptyState) return <>{emptyState}</>;

  return (
    <div className={styles.wrapper}>
      <table className={styles.table}>
        <caption className="visually-hidden">{caption}</caption>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key} scope="col" className={styles[column.align ?? 'left']}>
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={getRowKey(row)}>
              {columns.map((column) => (
                <td
                  key={column.key}
                  className={`${styles[column.align ?? 'left']} ${column.wrap ? styles.wrap : ''}`}
                >
                  {column.render(row, index)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

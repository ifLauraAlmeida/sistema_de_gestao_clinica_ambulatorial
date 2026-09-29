import { useState, type ReactElement } from 'react';
import { Search } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { SelectField } from '../../components/ui/SelectField';
import { TextField } from '../../components/ui/TextField';
import { searchServices } from '../../services/catalog';
import type { CatalogService } from '../../types/catalog';
import { describeService } from './agendaRules';
import styles from './AgendaPage.module.css';

interface ServicePickerProps {
  selected: CatalogService | undefined;
  error?: string;
  onSelect: (service: CatalogService | undefined) => void;
}

/** Busca no catálogo por nome ou sinônimo e seleção do serviço a agendar. */
export function ServicePicker({ selected, error, onSelect }: ServicePickerProps): ReactElement {
  const [search, setSearch] = useState('');
  const [results, setResults] = useState<CatalogService[] | null>(null);

  async function find(): Promise<void> {
    const found = await searchServices(search.trim());
    setResults(found);
    onSelect(found[0]);
  }

  return (
    <div className={styles.form}>
      <div className={styles.inline}>
        <TextField
          label="Buscar serviço"
          placeholder="Ex.: raio-x joelho, bioimpedância, ergometria"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter') {
              event.preventDefault();
              void find();
            }
          }}
        />
        <Button variant="secondary" icon={<Search size={16} />} onClick={() => void find()}>
          Buscar
        </Button>
      </div>
      {results && (
        <SelectField
          label="Serviço *"
          value={selected?.id ?? ''}
          placeholder={results.length ? undefined : 'Nenhum serviço encontrado'}
          options={results.map((service) => ({
            value: service.id,
            label: describeService(service),
          }))}
          onChange={(event) =>
            onSelect(results.find((service) => service.id === event.target.value))
          }
          error={error}
        />
      )}
      {selected?.preparation_instructions && (
        <p className={styles.preparation}>
          <strong>Preparo:</strong> {selected.preparation_instructions}
        </p>
      )}
    </div>
  );
}

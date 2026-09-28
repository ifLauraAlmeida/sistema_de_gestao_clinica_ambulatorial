import { useCallback, useState, type FormEvent, type ReactElement } from 'react';
import { ChevronLeft, ChevronRight, Pencil, Plus, Search, Users } from 'lucide-react';
import { Alert } from '../../components/ui/Alert';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { EmptyState } from '../../components/ui/EmptyState';
import { Loading } from '../../components/ui/Loading';
import { PageHeader } from '../../components/ui/PageHeader';
import { Table } from '../../components/ui/Table';
import { TextField } from '../../components/ui/TextField';
import { useApiResource } from '../../hooks/useApiResource';
import { useCurrentUser } from '../../hooks/useAuth';
import { getPatient, searchPatients } from '../../services/patients';
import type { PatientDemographics, PatientListItem } from '../../types/patient';
import { formatIsoDate } from '../../utils/dateTime';
import { describeError } from '../../utils/errorMessages';
import { hasAnyPermission } from '../../utils/userAccess';
import grid from '../../layouts/PageGrid.module.css';
import styles from './PatientsPage.module.css';
import { PatientForm } from './PatientForm';

type FormState =
  { mode: 'closed' } | { mode: 'create' } | { mode: 'edit'; patient: PatientDemographics };

/** Busca, cadastro e edição de pacientes (Tela 03). */
export function PatientsPage(): ReactElement {
  const user = useCurrentUser();
  const [searchInput, setSearchInput] = useState('');
  const [query, setQuery] = useState({ search: '', page: 1 });
  const [formState, setFormState] = useState<FormState>({ mode: 'closed' });
  const [feedback, setFeedback] = useState<{ tone: 'success' | 'error'; text: string } | null>(
    null,
  );
  const loader = useCallback(() => searchPatients(query.search, query.page), [query]);
  const patients = useApiResource(loader);
  const canCreate = hasAnyPermission(user, ['patient.create']);
  const canEdit = hasAnyPermission(user, ['patient.update_demographics']);

  function handleSearch(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault();
    setQuery({ search: searchInput.trim(), page: 1 });
  }

  async function openEdit(item: PatientListItem): Promise<void> {
    setFeedback(null);
    try {
      setFormState({ mode: 'edit', patient: await getPatient(item.id) });
    } catch (error) {
      setFeedback({
        tone: 'error',
        text: describeError(error, 'Não foi possível abrir o cadastro.'),
      });
    }
  }

  function handleSaved(patient: PatientDemographics, wasCreated: boolean): void {
    setFormState({ mode: 'closed' });
    setFeedback({
      tone: 'success',
      text: `Cadastro de ${patient.full_name} ${wasCreated ? 'criado' : 'atualizado'}.`,
    });
    void patients.reload();
  }

  const page = patients.data;
  const isFormOpen = formState.mode !== 'closed';

  return (
    <>
      <PageHeader
        title="Pacientes"
        subtitle="Pesquise, visualize e cadastre pacientes."
        actions={
          canCreate && (
            <Button icon={<Plus size={18} />} onClick={() => setFormState({ mode: 'create' })}>
              Novo paciente
            </Button>
          )
        }
      />
      {feedback && <Alert tone={feedback.tone}>{feedback.text}</Alert>}
      <div className={isFormOpen ? grid.columns : undefined}>
        <Card title="Cadastro de pacientes" icon={<Users size={20} />}>
          <form className={styles.searchBar} onSubmit={handleSearch} role="search">
            <TextField
              label="Buscar paciente"
              placeholder="Nome, CPF ou telefone"
              icon={<Search size={18} />}
              value={searchInput}
              onChange={(event) => setSearchInput(event.target.value)}
            />
            <Button type="submit" variant="secondary">
              Buscar
            </Button>
          </form>
          {patients.isLoading && <Loading />}
          {Boolean(patients.error) && (
            <Alert tone="error">Não foi possível carregar os pacientes.</Alert>
          )}
          {page && (
            <>
              <Table
                caption="Pacientes"
                rows={page.results}
                getRowKey={(patient) => patient.id}
                emptyState={
                  <EmptyState icon={<Users size={22} />} title="Nenhum paciente encontrado" />
                }
                columns={[
                  {
                    key: 'name',
                    header: 'Nome do paciente',
                    render: (p) => p.social_name || p.full_name,
                  },
                  { key: 'cpf', header: 'CPF', render: (p) => p.cpf_masked || '—' },
                  { key: 'phone', header: 'Telefone', render: (p) => p.phone || '—' },
                  {
                    key: 'birth',
                    header: 'Data de nasc.',
                    render: (p) => formatIsoDate(p.birth_date),
                  },
                  {
                    key: 'status',
                    header: 'Status',
                    render: (p) => (
                      <Badge tone={p.is_active ? 'success' : 'danger'}>
                        {p.is_active ? 'Ativo' : 'Inativo'}
                      </Badge>
                    ),
                  },
                  ...(canEdit
                    ? [
                        {
                          key: 'actions',
                          header: 'Ações',
                          render: (p: PatientListItem) => (
                            <Button
                              variant="ghost"
                              icon={<Pencil size={16} />}
                              onClick={() => void openEdit(p)}
                              aria-label={`Editar ${p.full_name}`}
                            >
                              Editar
                            </Button>
                          ),
                        },
                      ]
                    : []),
                ]}
              />
              <div className={styles.pagination}>
                <span>
                  {page.count} paciente{page.count === 1 ? '' : 's'} encontrado
                  {page.count === 1 ? '' : 's'}
                </span>
                <div className={styles.paginationButtons}>
                  <Button
                    variant="secondary"
                    icon={<ChevronLeft size={16} />}
                    disabled={!page.previous}
                    onClick={() => setQuery((q) => ({ ...q, page: q.page - 1 }))}
                  >
                    Anterior
                  </Button>
                  <Button
                    variant="secondary"
                    icon={<ChevronRight size={16} />}
                    disabled={!page.next}
                    onClick={() => setQuery((q) => ({ ...q, page: q.page + 1 }))}
                  >
                    Próxima
                  </Button>
                </div>
              </div>
            </>
          )}
        </Card>
        {isFormOpen && (
          <PatientForm
            key={formState.mode === 'edit' ? formState.patient.id : 'new'}
            patient={formState.mode === 'edit' ? formState.patient : null}
            onSaved={handleSaved}
            onClose={() => setFormState({ mode: 'closed' })}
          />
        )}
      </div>
    </>
  );
}

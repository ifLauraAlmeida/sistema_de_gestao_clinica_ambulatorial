# Sistema de Gestão Clínica Ambulatorial

Aplicação web para digitalização e gestão de fluxos administrativos e assistenciais de clínicas, centros médicos e serviços ambulatoriais.

O projeto centraliza operações que normalmente ficam distribuídas entre fichas físicas, planilhas, filas manuais e sistemas isolados, mantendo uma arquitetura simples, auditável e preparada para crescimento.

O escopo funcional completo está em [`references/escopo_sistema.md`](references/escopo_sistema.md). As referências visuais ficam em [`references/inspiracao_design/`](references/inspiracao_design/). Regras de desenvolvimento: [`AGENTS.md`](AGENTS.md). Convenção de commits: [`commit_conventionals.md`](commit_conventionals.md).

---

## Status

**Etapa 1 — Fundação** (concluída):

- monorepo com `backend/` (Django + DRF) e `frontend/` (React + TypeScript + Vite);
- PostgreSQL como banco oficial e Redis preparado para tempo real (Django Channels);
- Custom User Model com perfis **ATENDENTE**, **MEDICO** e **GESTOR**;
- RBAC com permissões granulares + autorização contextual no backend;
- sessão de trabalho (guichê/consultório) obrigatória para atendente e médico;
- check-in, fila da recepção, fila clínica ativa/inativa, chamadas com destino histórico;
- acesso contextual ao prontuário (somente enquanto o paciente está na fila ativa do médico);
- auditoria imutável (inclusive de tentativas negadas);
- login, layout principal e dashboard por perfil;
- testes automatizados (incluindo os 30 cenários de autorização), lint e Docker.

**Ainda não implementado** (próximas etapas): telas de pacientes/agenda/check-in, prontuário completo, prescrição, documentos e assinatura, financeiro e convênios, painel público e eventos WebSocket, relatórios, integrações externas, multiunidade.

---

## Stack

| Camada | Tecnologias |
|---|---|
| Backend | Python 3.13, Django 6.1, Django REST Framework, Daphne (ASGI) |
| Banco de dados | PostgreSQL 17 |
| Tempo real (preparado) | Django Channels, Redis 7, WebSocket |
| Frontend | React 19, TypeScript, Vite, React Router, lucide-react |
| Qualidade | pytest, Ruff, mypy (django-stubs), Vitest, Testing Library, ESLint, Prettier |
| Infraestrutura | Docker, Docker Compose, Linux; Nginx como proxy reverso em produção |

---

## Arquitetura

```text
NAVEGADOR (React)
      │  HTTP (cookie de sessão + CSRF)        WebSocket (futuro)
      ▼                                              │
Vite dev server (dev) / Nginx (produção)  ── /api ───┤
      │                                              │
      ▼                                              ▼
Django + DRF (ASGI / Daphne)  ─────────────────  Channels ── Redis
      │
      ▼
PostgreSQL (fonte oficial de verdade)
```

Frontend e API são servidos na **mesma origem**: em desenvolvimento o Vite encaminha `/api` para o Django; em produção o Nginx fará o mesmo papel. Assim o cookie de sessão (HttpOnly) e a proteção CSRF funcionam sem CORS e sem tokens no `localStorage`.

### Organização do backend

Cada domínio é um app Django em `backend/apps/`. Views apenas coordenam (validam entrada, verificam autorização, chamam serviço, respondem); regras ficam em `services`, consultas em `selectors` e decisões de autorização contextual em `policies`.

| App | Responsabilidade |
|---|---|
| `core` | health check, formato padronizado de erros, autenticação por sessão, logs JSON |
| `accounts` | usuário, perfis, matriz de permissões, login/logout/me |
| `audit` | eventos de auditoria imutáveis e consulta pelo gestor |
| `workstations` | guichês/consultórios (`Station`) e sessões de trabalho (`WorkSession`) |
| `patients` | cadastro único de pacientes (CPF validado, único e mascarado em listagens) |
| `professionals` | profissionais e especialidades (prefixo das senhas) |
| `scheduling` | agendamentos |
| `encounters` | check-in, atendimento, histórico de status, finalização (ATENDIDO) |
| `queues` | fila da recepção, fila clínica, chamadas (`QueueCall`) e encaminhamento |
| `medical_records` | evolução clínica mínima e política de acesso ao prontuário |
| `demo_data` | comando de dados fictícios para desenvolvimento |

### Organização do frontend

```text
frontend/src/
├── app/          # rotas, provedor de autenticação, guardas de rota, menu
├── components/ui # design system (Button, TextField, Card, Badge, KpiCard, Table…)
├── layouts/      # MainLayout, Sidebar, Topbar
├── pages/        # login, seleção de posto, dashboards por perfil
├── services/     # único ponto de comunicação HTTP (api.ts, auth.ts, workSession.ts, queues.ts)
├── hooks/        # useAuth, useApiResource, useQueueOperation, useNow
├── types/        # contratos da API
├── utils/        # funções puras (métricas de fila, datas, permissões de exibição)
├── styles/       # tokens de design e estilos globais
└── test/         # FakeBackend, fixtures e utilitários de teste
```

---

## Estrutura do monorepo

```text
.
├── AGENTS.md                 # padrões de desenvolvimento
├── commit_conventionals.md   # convenção de commits
├── README.md
├── Makefile                  # comandos oficiais (execução, testes, lint)
├── docker-compose.yml        # postgres, redis, backend e frontend
├── .env.example              # variáveis de ambiente (sem segredos)
├── backend/
│   ├── manage.py
│   ├── pyproject.toml        # dependências e configuração de ruff, mypy e pytest
│   ├── Dockerfile
│   ├── config/               # settings por ambiente, urls, asgi, wsgi
│   ├── apps/                 # domínios
│   └── tests/                # cenários de autorização entre domínios
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── Dockerfile
│   └── src/
└── references/               # escopo e referências visuais (documentação permanente)
```

---

## Como executar

Pré-requisitos: **Docker** e **Docker Compose** (e `make`, opcional). Em hosts com SELinux (ex.: Fedora) os volumes já usam o sufixo `:z`.

### 1. Variáveis de ambiente

```bash
cp .env.example .env
```

Preencha no `.env`:

- `DJANGO_SECRET_KEY` — gere com `python3 -c "import secrets; print(secrets.token_urlsafe(50))"`;
- `POSTGRES_PASSWORD` — senha local do banco;
- `DEMO_USERS_PASSWORD` — (opcional) senha dos usuários fictícios de demonstração, mínimo de 10 caracteres.

O `.env` nunca deve ser versionado (já está no `.gitignore`).

### 2. Subir os serviços

```bash
docker compose up --build
# ou: make up
```

O backend aplica as migrations automaticamente ao iniciar.

| Serviço | Endereço |
|---|---|
| Frontend (Vite) | http://localhost:5173 |
| API | http://localhost:8000/api/v1/ (também via http://localhost:5173/api/v1/) |
| Django admin | http://localhost:8000/admin/ |
| Health check | http://localhost:8000/api/v1/health/ |

PostgreSQL e Redis não são expostos no host; ficam acessíveis apenas na rede do Compose.

### 3. Dados fictícios de demonstração (opcional)

```bash
make seed
# ou: docker compose run --rm backend python manage.py seed_demo_data --password "<senha>"
```

Cria usuários `recepcao.demo` (atendente), `medica.demo` e `medico.demo` (médicos), `gestao.demo` (gestor), guichês, consultórios, especialidades, pacientes **fictícios** (sem CPF) e a agenda do dia com parte dos pacientes em fila. O comando recusa execução com `DJANGO_DEBUG=false`.

### 4. Superusuário

```bash
make createsuperuser
# ou: docker compose run --rm backend python manage.py createsuperuser
```

Superusuários são criados com perfil **GESTOR**. Pelo `/admin/` o gestor cadastra usuários, guichês/consultórios (`Postos de trabalho`), especialidades e profissionais.

### Migrations

```bash
make makemigrations   # gera migrations após alterar models
make migrate          # aplica migrations
```

Toda migration é versionada. O Custom User existe desde a primeira migration de `accounts`.

### Executar fora do Docker (opcional)

- **Frontend**: `cd frontend && npm install && VITE_BACKEND_URL=http://localhost:8000 npm run dev`.
- **Backend**: requer Python 3.12+ e acesso a um PostgreSQL/Redis (ajuste `POSTGRES_HOST`/`REDIS_URL` no `.env` para `localhost` e publique as portas com um `docker-compose.override.yml`); depois `cd backend && pip install -e ".[dev]" && python manage.py runserver`.

---

## Testes, lint e build

Comando oficial (executa tudo nos containers):

```bash
make test     # backend (pytest) + frontend (vitest)
make lint     # ruff, formatação, mypy, migrations pendentes, eslint, prettier, tsc
make check    # lint + testes + build do frontend
```

Comandos individuais:

```bash
docker compose run --rm backend pytest
docker compose run --rm backend sh -c "ruff check . && ruff format --check . && mypy ."
docker compose run --rm --no-deps frontend npm test
docker compose run --rm --no-deps frontend npm run lint
docker compose run --rm --no-deps frontend npm run build
```

Os testes do backend usam **PostgreSQL** (as mesmas constraints e triggers de produção). Os cenários de autorização exigidos estão em `backend/tests/test_authorization_scenarios.py`, numerados de 1 a 30.

---

## Variáveis de ambiente

| Variável | Uso |
|---|---|
| `DJANGO_SECRET_KEY` | chave secreta do Django (obrigatória) |
| `DJANGO_DEBUG` | `true` apenas em desenvolvimento |
| `DJANGO_ALLOWED_HOSTS` | hosts aceitos (separados por vírgula) |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | origens confiáveis para CSRF (ex.: `http://localhost:5173`) |
| `DJANGO_SETTINGS_MODULE` | não definir em dev (padrão `config.settings.development`); em produção `config.settings.production` |
| `DJANGO_LOG_LEVEL` | nível dos logs JSON |
| `SESSION_IDLE_TIMEOUT_SECONDS` | expiração da sessão por inatividade (padrão 1800) |
| `LOGIN_THROTTLE_RATE` | limite de tentativas de login (padrão `10/min`) |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT` | conexão com o PostgreSQL |
| `REDIS_URL` | Redis do Channels |
| `DEMO_USERS_PASSWORD` | senha dos usuários fictícios (`make seed`) |
| `VITE_BACKEND_URL` | destino do proxy `/api` do Vite |

---

## Autenticação

- Sessão/cookie do Django (`sessionid` HttpOnly, `SameSite=Lax`); nenhum token ou credencial no `localStorage`.
- CSRF obrigatório em toda escrita, inclusive no login: o frontend obtém o cookie em `GET /api/v1/auth/csrf/` e envia `X-CSRFToken`.
- Sessão expira por inatividade (computadores compartilhados); login com limite de tentativas.
- Respostas: `401` sem sessão, `403` sem permissão.

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/v1/health/` | verifica PostgreSQL e Redis sem expor detalhes |
| GET | `/api/v1/auth/csrf/` | define o cookie CSRF |
| POST | `/api/v1/auth/login/` | login (`username`, `password`) |
| POST | `/api/v1/auth/logout/` | logout (encerra também a sessão de trabalho) |
| GET | `/api/v1/auth/me/` | usuário, perfil, permissões, posto exigido e sessão de trabalho |

Erros seguem sempre o formato:

```json
{ "error": { "code": "medical_record_access_denied", "message": "Acesso ao prontuário não autorizado para este atendimento." } }
```

---

## Perfis e permissões

A autorização real acontece **sempre no backend**. O frontend recebe a lista de permissões apenas para montar menu e telas; ocultar um botão não é segurança.

1. **RBAC** — `apps/accounts/access_permissions.py` mapeia cada perfil para permissões granulares (`patient.create`, `reception_queue.call`, `clinical_queue.call_own`, `medical_record.view_active_patient`, `audit.view`…). Endpoints declaram `required_permissions`; métodos não declarados são negados (negado por padrão) e negações são auditadas.
2. **Autorização contextual** — políticas por domínio decidem o que depende de contexto:
   - `queues/policies.py`: médico só consulta e chama a **própria** fila, na especialidade em que atende; chamadas exigem sessão de trabalho no tipo de posto correto;
   - `medical_records/policies.py`: prontuário/histórico só enquanto o atendimento do paciente está na **fila ativa** do médico; finalizar como ATENDIDO revoga esse vínculo (os registros permanecem);
   - `workstations/policies.py`: atendente ocupa guichês; médico ocupa consultórios.

| Funcionalidade | Atendente | Médico | Gestor |
|---|---|---|---|
| Criar paciente / dados cadastrais | sim | não (vê identificação no prontuário) | sim |
| Agenda | sim | não (futuro/contextual) | sim |
| Check-in, fila da recepção, chamar para guichê | sim | não | sim |
| Fila clínica própria (ativa/inativa), chamar para consultório | não | sim (própria) | sim (todas) |
| Prontuário e histórico clínico | não | somente fila ativa | sim (auditado) |
| Registrar evolução, finalizar atendimento | não | sim (próprio atendimento) | não¹ |
| Histórico financeiro, indicadores gerais, auditoria, usuários | não | não | sim |

¹ Decisão: o gestor tem acesso administrativo total, mas atos clínicos (evolução e ATENDIDO) permanecem exclusivos do médico responsável.

---

## Sessão de trabalho (guichê e consultório)

Guichê e consultório **não** são atributos do usuário. Após o login, atendente e médico escolhem o posto em `/workstation`, o que cria uma `WorkSession` (`user`, `station`, `station_type`, `started_at`, `ended_at`). Regras:

- uma sessão aberta por usuário (constraint no banco); trocar de posto encerra a anterior;
- login e logout encerram sessões esquecidas abertas (cada login exige nova seleção);
- chamadas exigem sessão aberta no tipo de posto da fila (guichê para recepção, consultório para fila clínica);
- cada `QueueCall` grava `destination_type`, `destination_id` e `destination_label` como **snapshot**: trocar de posto depois não altera o histórico ("GINE04 chamada para Consultório 03 às 14:32" continua verdadeiro).

| Método | Endpoint |
|---|---|
| GET | `/api/v1/work-sessions/stations/` |
| POST | `/api/v1/work-sessions/` (`station_id`) |
| GET | `/api/v1/work-sessions/current/` |
| POST | `/api/v1/work-sessions/current/end/` |

### Demais endpoints desta etapa

| Método | Endpoint | Permissão |
|---|---|---|
| GET/POST | `/api/v1/patients/` | `patient.view_demographics` / `patient.create` |
| GET/PATCH | `/api/v1/patients/{id}/` | `patient.view_demographics` / `patient.update_demographics` |
| GET/POST | `/api/v1/appointments/` | `appointment.view` / `appointment.create` |
| PATCH | `/api/v1/appointments/{id}/` | `appointment.update` |
| POST | `/api/v1/check-ins/` | `checkin.create` |
| GET | `/api/v1/reception-queue/`, `/api/v1/reception-queue/calls/` | `reception_queue.view` |
| POST | `/api/v1/reception-queue/{id}/call/` | `reception_queue.call` + guichê |
| POST | `/api/v1/reception-queue/{id}/forward/` | `reception_queue.forward` |
| GET | `/api/v1/clinical-queue/?status=active\|inactive` | própria fila ou todas (gestor) |
| POST | `/api/v1/clinical-queue/{id}/call/` | própria fila + consultório |
| POST | `/api/v1/encounters/{id}/complete/` | médico responsável |
| GET | `/api/v1/encounters/{id}/medical-record/`, `/clinical-history/` | política contextual |
| POST | `/api/v1/encounters/{id}/clinical-notes/` | política contextual |
| GET | `/api/v1/audit/events/` | `audit.view` |

---

## Auditoria

`AuditEvent` registra quem, o quê, quando, IP e metadados (estado anterior/novo quando aplicável). Eventos: `LOGIN_SUCCESS`, `LOGIN_FAILED`, `LOGOUT`, `ACCESS_DENIED`, `WORK_SESSION_STARTED/ENDED`, `PATIENT_CREATED/UPDATED`, `APPOINTMENT_CREATED/UPDATED`, `CHECK_IN_CREATED`, `ENCOUNTER_STATUS_CHANGED`, `ENCOUNTER_COMPLETED`, `QUEUE_TICKET_CALLED`, `QUEUE_ENTRY_FORWARDED`, `MEDICAL_RECORD_VIEW_GRANTED/DENIED`, `CLINICAL_NOTE_CREATED`.

- Imutável: bloqueado no model e por **trigger no PostgreSQL** (UPDATE/DELETE).
- Negações são gravadas fora da transação da operação, para não serem desfeitas pelo rollback.
- Metadados nunca contêm senha, CPF completo ou conteúdo clínico.

---

## Principais decisões arquiteturais

- **React + DRF em vez de Django Templates/HTMX** (sugestão inicial do escopo): definido para esta fase do projeto; o backend continua organizado por domínio e pode servir outras interfaces.
- **Sessão/cookie na mesma origem** em vez de JWT: aplicação interna, cookies HttpOnly e CSRF nativos do Django, nada sensível em `localStorage`.
- **Permissões em código (StrEnum) em vez de tabelas de Role/Permission**: matriz versionada e testável; migrar para tabelas quando houver necessidade real de configuração pelo gestor.
- **UUID** como chave primária dos registros de domínio; CPF nunca é chave.
- **Constraints no banco** para invariantes críticas (perfil válido, uma sessão aberta por usuário, uma entrada ativa por fila, senha diária única, CPF único, atendimento ATENDIDO com horário de finalização).
- **Fila ≠ chamada**: `QueueEntry` guarda o estado; `QueueCall` é o evento, com destino em snapshot e número de tentativa (rechamadas).
- **Postos compartilháveis**: dois usuários podem abrir sessão no mesmo guichê, evitando bloqueio por sessões esquecidas; revisar quando o painel público exigir exclusividade.
- **Atualização das filas por polling (15 s)** no frontend como solução provisória; Channels + Redis já estão configurados no ASGI para os eventos em tempo real da próxima etapa.
- **Dados de demonstração** apenas fictícios, gerados por comando que recusa execução fora de DEBUG.

---

## Produção (preparação)

- `config.settings.production`: `DEBUG=False`, cookies `Secure`, HSTS, redirecionamento HTTPS e cabeçalho `X-Forwarded-Proto` do proxy.
- A imagem do backend executa `daphne config.asgi:application` por padrão.
- Nginx (a configurar) servirá o build estático do frontend e encaminhará `/api`, `/admin` e `/ws` ao backend na mesma origem; arquivos estáticos do admin via `collectstatic`.

---

## Segurança e dados sensíveis

Nunca versionar `.env`, credenciais, certificados privados, dumps ou dados de pacientes. Utilizar apenas dados fictícios em desenvolvimento e testes. Logs técnicos são estruturados em JSON e não registram senhas, tokens, CPF completo ou conteúdo clínico.

---

## Licença

Definir antes da primeira distribuição externa.

Caso o sistema seja comercializado como produto proprietário, não adicionar automaticamente uma licença open source ao repositório.

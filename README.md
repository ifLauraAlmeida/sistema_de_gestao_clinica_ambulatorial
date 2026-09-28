# Sistema de Gestão Clínica Ambulatorial

Aplicação web para digitalização e gestão de fluxos administrativos e assistenciais de clínicas, centros médicos e serviços ambulatoriais.

O projeto foi concebido para centralizar operações que normalmente ficam distribuídas entre fichas físicas, planilhas, filas manuais e sistemas isolados, mantendo uma arquitetura simples, auditável e preparada para crescimento.

---

## Objetivo

O **Sistema de Gestão Clínica Ambulatorial (SGCA)** deverá permitir:

- cadastro único de pacientes;
- cadastro de profissionais e especialidades;
- agenda e marcações;
- check-in;
- controle de filas;
- chamadas em tempo real;
- painel público de senhas;
- prontuário eletrônico;
- evolução clínica;
- emissão de documentos;
- autorizações de convênios;
- pagamentos;
- relatórios e indicadores;
- auditoria;
- controle de acesso por perfil.

A proposta é priorizar uma experiência simples para recepção, profissionais de saúde e gestão, sem exigir uma arquitetura excessivamente complexa.

---

## Stack principal

### Backend
- Python
- Django

### Banco de dados
- PostgreSQL

### Frontend
- Django Templates
- HTML
- CSS
- Bootstrap
- HTMX

### Tempo real
- Django Channels
- WebSocket
- Redis

### Infraestrutura
- Linux
- Docker
- Docker Compose
- Nginx
- ASGI

### Controle de versão
- Git
- GitHub

---

## Arquitetura

```text
NAVEGADORES / PAINÉIS
        │
        ├── HTTP/HTTPS
        └── WebSocket
        │
        ▼
      Nginx
        │
        ▼
      Django
        │
        ├── autenticação
        ├── pacientes
        ├── profissionais
        ├── agenda
        ├── check-in
        ├── filas
        ├── chamadas
        ├── prontuário
        ├── documentos
        ├── financeiro
        ├── relatórios
        └── auditoria
        │
        ├──────────────► Redis
        │
        ▼
   PostgreSQL
```

---

## Estrutura sugerida

```text
sgca/
│
├── config/
│   ├── settings/
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── accounts/
├── patients/
├── professionals/
├── specialties/
├── scheduling/
├── checkin/
├── queues/
├── calls/
├── encounters/
├── medical_records/
├── documents/
├── billing/
├── insurance/
├── reports/
├── audit/
├── core/
│
├── templates/
├── static/
├── media/
├── tests/
├── docker/
├── docker-compose.yml
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Organização por domínio

O projeto deve evitar concentrar toda a lógica em um único módulo. Cada domínio possui responsabilidade própria.

### `accounts`
Usuários, autenticação, perfis, permissões e sessões.

### `patients`
Cadastro do paciente, busca, atualização cadastral, prevenção de duplicidades e histórico administrativo.

### `professionals`
Profissionais, conselhos, especialidades e vínculos.

### `scheduling`
Agendas, horários, agendamentos, retornos, encaixes e bloqueios.

### `checkin`
Confirmação de chegada, identificação do atendimento e encaminhamento para autorização ou fila.

### `queues`
Entrada em fila, posição, prioridade, status e tempo de espera.

### `calls`
Geração de senhas, chamada, rechamada, destino, painel público e eventos em tempo real.

### `encounters`
Criação, início, encerramento e vínculo entre paciente e profissional.

### `medical_records`
Prontuário, evolução, diagnóstico, conduta e histórico clínico.

### `documents`
Receitas, atestados, relatórios, encaminhamentos, solicitações e assinaturas.

### `billing`
Pagamentos, comandas, valores e formas de pagamento.

### `insurance`
Convênios, carteirinhas, autorizações e guias.

### `reports`
Indicadores, dashboards e relatórios administrativos.

### `audit`
Logs, acessos, alterações e rastreabilidade.

---

## Modelagem inicial

Entidades principais:

```text
User
Role
Permission

Patient
PatientInsurance

Professional
Specialty
ProfessionalSpecialty

Schedule
Appointment

Encounter
QueueEntry
QueueCall

MedicalRecord
ClinicalNote
Diagnosis
Prescription

Document
DocumentSignature

Payment
InsuranceAuthorization

AuditEvent
```

### Regra central de modelagem

Paciente, atendimento e registro clínico devem ser entidades distintas.

```text
Patient
   │
   ├── Appointment
   │
   └── Encounter
          │
          ├── QueueEntry
          ├── QueueCall
          ├── ClinicalNote
          ├── Diagnosis
          ├── Document
          └── Payment
```

O cadastro do paciente não deve armazenar diretamente os dados de cada consulta.

---

## Autenticação e permissões

O sistema deve utilizar controle de acesso baseado em funções e, quando necessário, regras contextuais.

Exemplos:

```text
patient.view
patient.create
patient.update
appointment.view
appointment.create
appointment.cancel
queue.view
queue.manage
medical_record.view
medical_record.update
document.create
document.sign
billing.view
billing.update
report.view
user.manage
```

Exemplo de acesso contextual:

```text
Profissional autenticado
        ↓
Paciente está vinculado ao atendimento?
        ↓
SIM
        ↓
Acesso permitido
```

Tentativas de acesso indevido deverão ser registradas.

---

## Tempo real

O sistema utilizará WebSocket nas funcionalidades que exigem atualização imediata:

- atualização de filas;
- chamadas de senha;
- painel público;
- entrada de paciente na fila;
- atualização da fila do profissional;
- dashboards operacionais.

```text
Django
   │
   ▼
Django Channels
   │
   ▼
Redis
   │
   ▼
WebSocket
   │
   ├── recepção
   ├── consultório
   └── painel público
```

---

## Painel público

O painel de chamadas será uma página web do próprio sistema.

Exemplos:

```text
/painel/recepcao/
/painel/consultorios/
```

A tela poderá permanecer aberta em modo kiosk.

```text
SENHA ATUAL

GINE01

CONSULTÓRIO 04
```

O painel não deverá exibir nome, CPF, diagnóstico ou outros dados pessoais desnecessários.

---

## Banco de dados

Banco principal:

```text
PostgreSQL
```

Diretrizes:

- utilizar UUID quando apropriado;
- utilizar chaves estrangeiras;
- criar constraints;
- criar índices para consultas frequentes;
- não utilizar CPF como chave primária;
- evitar exclusão física de registros clínicos;
- utilizar transações em operações críticas.

---

## Arquivos e anexos

Documentos binários não devem ser armazenados diretamente no PostgreSQL. O banco deverá guardar metadados e referências.

```text
id
patient_id
encounter_id
path
filename
content_type
hash
created_at
created_by
```

Possíveis storages:

- filesystem local;
- MinIO;
- S3;
- Google Cloud Storage.

---

## Auditoria

Auditoria faz parte da arquitetura desde o início.

```text
AuditEvent

id
user_id
action
entity_type
entity_id
timestamp
ip_address
metadata
```

Eventos relevantes incluem login, logout, consulta a prontuário, alteração cadastral, criação de atendimento, alteração de fila, emissão de documento, assinatura, pagamento e alteração de permissão.

---

## Segurança

Requisitos mínimos:

- HTTPS;
- hash seguro de senhas;
- proteção CSRF;
- proteção XSS;
- prevenção de SQL Injection;
- timeout de sessão;
- controle de acesso no backend;
- contas individuais;
- logs de auditoria;
- backup e restauração;
- cookies seguros;
- proteção de variáveis de ambiente.

Nunca versionar:

- `.env`;
- credenciais;
- certificados privados;
- dumps de produção;
- dados de pacientes.

---

## Desenvolvimento local

### 1. Clone

```bash
git clone <URL_DO_REPOSITORIO>
cd <DIRETORIO_DO_PROJETO>
```

### 2. Variáveis de ambiente

```bash
cp .env.example .env
```

### 3. Subir os serviços

```bash
docker compose up -d
```

### 4. Executar migrations

```bash
docker compose exec web python manage.py migrate
```

### 5. Criar usuário administrativo

```bash
docker compose exec web python manage.py createsuperuser
```

### 6. Acessar

```text
http://localhost:8000
```

---

## Serviços esperados no Docker Compose

```text
web
postgres
redis
nginx
```

Durante desenvolvimento, o Nginx poderá ser opcional.

---

## Variáveis de ambiente

Exemplo de `.env.example`:

```env
DJANGO_SECRET_KEY=
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=sgca
POSTGRES_USER=sgca
POSTGRES_PASSWORD=
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

REDIS_URL=redis://redis:6379/0
```

---

## Testes

O projeto deverá possuir testes automatizados para regras críticas, principalmente permissões, criação de atendimento, check-in, fila, chamadas, prontuário, documentos, auditoria, pagamentos e transições de status.

```bash
python manage.py test
```

Caso seja adotado `pytest`:

```bash
pytest
```

---

## Qualidade de código

Diretrizes:

- funções pequenas;
- responsabilidades bem definidas;
- regras de negócio fora das views;
- evitar duplicação;
- nomes explícitos;
- tipagem sempre que possível;
- migrations versionadas;
- testes para regras críticas.

Estrutura sugerida dentro de um domínio:

```text
patients/
├── models.py
├── services.py
├── selectors.py
├── forms.py
├── views.py
├── urls.py
├── tests/
└── templates/
```

`services.py` concentra operações que alteram estado; `selectors.py`, consultas de leitura.

---

## Ordem sugerida de implementação

### Fase 1 — Base
- projeto Django;
- PostgreSQL;
- Docker;
- autenticação;
- usuários;
- permissões;
- auditoria básica.

### Fase 2 — Cadastros
- pacientes;
- profissionais;
- especialidades;
- convênios.

### Fase 3 — Agenda
- grade;
- disponibilidade;
- agendamentos;
- retornos;
- encaixes.

### Fase 4 — Check-in
- chegada;
- confirmação;
- identificação do atendimento;
- encaminhamento.

### Fase 5 — Filas
- fila;
- prioridade;
- estados;
- tempo de espera.

### Fase 6 — Chamadas
- geração de senha;
- chamada;
- rechamada;
- WebSocket;
- painel público.

### Fase 7 — Atendimento
- abertura;
- profissional responsável;
- início;
- finalização.

### Fase 8 — Prontuário
- evolução;
- histórico;
- diagnósticos;
- condutas.

### Fase 9 — Documentos
- receita;
- atestado;
- relatório;
- encaminhamento;
- assinatura.

### Fase 10 — Financeiro
- particular;
- convênios;
- autorizações;
- pagamentos.

### Fase 11 — Indicadores
- dashboards;
- relatórios;
- exportações.

### Fase 12 — Hardening
- revisão de segurança;
- backup;
- restauração;
- observabilidade;
- testes de carga;
- revisão de permissões.

---

## Escopo detalhado

O documento completo de requisitos e regras de negócio está em:

```text
escopo_sistema_cmeg.md
```

O nome do arquivo é mantido conforme solicitado, porém o conteúdo descreve um produto genérico e reutilizável.

---

## Status do projeto

```text
Em planejamento / prototipação
```

---

## Licença

Definir antes da primeira distribuição externa.

Caso o sistema seja comercializado como produto proprietário, não adicionar automaticamente uma licença open source ao repositório.

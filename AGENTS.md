# Padrões de desenvolvimento

Este documento define as regras que devem ser seguidas por qualquer pessoa ou agente de IA ao criar, modificar, refatorar ou revisar código neste projeto.

O objetivo é manter o sistema previsível, modular, testável e fácil de manter.

As regras deste arquivo devem ser consideradas durante todo o desenvolvimento.

---

## Estilo de código

- Funções devem normalmente ter entre 4 e 20 linhas.
- Funções maiores devem ser divididas quando executarem mais de uma responsabilidade.
- Não dividir uma lógica coesa apenas para satisfazer um limite arbitrário de linhas.
- Arquivos devem normalmente possuir menos de 500 linhas.
- Arquivos maiores devem ser divididos por responsabilidade, domínio ou contexto.
- Coesão é mais importante do que limites rígidos de tamanho.
- Cada função deve possuir uma única responsabilidade.
- Cada módulo deve possuir uma responsabilidade claramente identificável.
- Seguir o princípio de responsabilidade única — SRP.
- Evitar arquivos genéricos que concentrem funcionalidades não relacionadas.

Evitar nomes genéricos como:

```text
data
handler
manager
helper
utils
common
process
```

Preferir nomes específicos ao domínio e à responsabilidade.

Exemplo:

```text
call_queue_ticket
calculate_waiting_time
create_patient_record
close_attendance
validate_room_availability
```

Sempre que possível, utilizar nomes que retornem poucos resultados ao pesquisar no código.

---

## Tipagem

- Utilizar tipagem explícita.
- Não utilizar `any`.
- Não utilizar tipos genéricos excessivamente amplos.
- Não criar funções sem tipos quando a linguagem permitir tipagem.
- Tipar parâmetros e retornos de funções.
- Preferir tipos específicos do domínio.

Evitar:

```python
def process(data):
    ...
```

Preferir:

```python
def call_queue_ticket(ticket_id: int, room_id: int) -> QueueTicket:
    ...
```

---

## Duplicação

Não duplicar código.

Quando a mesma lógica surgir em mais de um local:

1. identificar a responsabilidade comum;
2. extrair a lógica;
3. criar função, serviço ou componente reutilizável;
4. manter um único ponto de implementação.

Não criar abstrações prematuras para códigos que apenas parecem semelhantes.

A abstração deve representar uma responsabilidade real do domínio.

---

## Fluxo de controle

Preferir retornos antecipados em vez de muitos níveis de condicionais.

Evitar:

```python
if user:
    if user.is_active:
        if user.has_permission:
            ...
```

Preferir:

```python
if user is None:
    return

if not user.is_active:
    return

if not user.has_permission:
    return
```

Máximo recomendado:

```text
2 níveis de indentação lógica
```

Caso seja necessário ultrapassar esse limite frequentemente, considerar dividir a responsabilidade.

---

## Exceções

Mensagens de exceção devem informar:

- o valor recebido;
- o valor ou formato esperado;
- contexto suficiente para localizar o problema.

Evitar:

```text
valor inválido
```

Preferir:

```text
status inválido: recebido='waiting', esperado um dos valores:
aguardando, chamado, atendimento ou finalizado
```

Não expor exceções internas diretamente para usuários finais.

---

# Comentários

Comentários devem explicar **por que algo existe**, e não simplesmente repetir o código.

Evitar:

```python
# incrementa o contador
counter += 1
```

Preferir:

```python
# Senhas já chamadas não voltam para a posição anterior da fila.
counter += 1
```

---

## Preservação de comentários

Comentários existentes não devem ser removidos automaticamente durante refatorações.

Eles podem conter:

- contexto histórico;
- decisões arquiteturais;
- limitações externas;
- comportamento de integrações;
- motivos de implementação.

Caso um comentário esteja incorreto ou obsoleto, atualizar seu conteúdo em vez de simplesmente removê-lo.

---

## Docstrings

Funções públicas devem possuir docstrings contendo:

- objetivo da função;
- comportamento relevante;
- pelo menos um exemplo de utilização quando fizer sentido.

Exemplo:

```python
def call_queue_ticket(ticket_id: int, room_id: int) -> QueueTicket:
    """
    Chama uma senha para atendimento em uma sala específica.

    Exemplo:
        call_queue_ticket(ticket_id=12, room_id=4)
    """
```

---

## Referências técnicas

Quando uma linha ou implementação existir devido a:

- bug específico;
- limitação de biblioteca;
- incompatibilidade externa;
- comportamento temporário;
- problema conhecido;

registrar quando possível:

```text
issue
commit
pull request
documentação relacionada
```

Exemplo:

```python
# Mantido devido ao comportamento registrado na issue #142.
```

---

# Testes

Os testes devem executar por meio de um único comando definido pelo projeto.

Exemplo:

```bash
pytest
```

ou:

```bash
make test
```

O comando oficial deve estar documentado no `README.md`.

---

## Regras de testes

Toda nova regra de negócio deve possuir teste.

Correções de bugs devem possuir teste de regressão sempre que possível.

Testes devem seguir o princípio F.I.R.S.T.:

- Fast — rápidos;
- Independent — independentes;
- Repeatable — repetíveis;
- Self-validating — autoavaliáveis;
- Timely — criados junto da funcionalidade.

---

## Prioridade de testes

Priorizar testes para:

- autenticação;
- autorização;
- permissões;
- filas;
- senhas;
- chamadas de atendimento;
- agendamentos;
- pacientes;
- profissionais;
- histórico de atendimento;
- auditoria;
- integrações externas;
- regras que modificam estados importantes do sistema.

---

## Dependências externas em testes

APIs, banco de dados externo, filesystem, serviços externos e integrações devem ser simulados quando necessário.

Preferir classes falsas nomeadas.

Exemplo:

```text
FakeSmsGateway
FakeNotificationService
FakeQueueDisplay
```

Evitar mocks inline excessivamente complexos.

---

# Dependências

Dependências devem ser injetadas por:

- construtor;
- parâmetro;
- configuração explícita.

Evitar dependências escondidas em variáveis globais.

---

## Bibliotecas externas

Bibliotecas de terceiros devem ser encapsuladas quando representarem uma integração importante.

Exemplo:

```text
notifications/
    sms_gateway.py
```

Em vez de espalhar chamadas diretas ao provedor por diversos módulos.

Isso permite trocar futuramente:

```text
Twilio
Zenvia
WhatsApp
SMS
E-mail
```

sem alterar regras internas do sistema.

---

# Estrutura do projeto

Seguir primeiro as convenções do framework utilizado.

Para Django, preferir a estrutura padrão do framework antes de criar abstrações personalizadas.

Evitar arquiteturas complexas sem necessidade concreta.

Preferir pequenos módulos focados.

---

# Django

Seguir as convenções do Django antes de criar soluções próprias.

Views devem coordenar requisições.

Views não devem concentrar regras de negócio.

Evitar:

```python
def atendimento_view(request):
    # autenticação
    # criação de senha
    # busca do paciente
    # envio de websocket
    # auditoria
    # alteração do atendimento
    # envio de notificação
```

Preferir distribuir responsabilidades entre módulos apropriados.

---

## Models

Models representam estado e comportamento relacionado diretamente à entidade.

Evitar modelos gigantes com dezenas de responsabilidades.

Regras complexas envolvendo múltiplas entidades devem ser colocadas em serviços específicos.

---

## Services

Operações de negócio devem possuir serviços focados quando envolverem múltiplas etapas.

Exemplo:

```text
queue/
    services/
        create_ticket.py
        call_ticket.py
        recall_ticket.py
        finish_ticket.py
```

Cada serviço deve possuir uma responsabilidade clara.

---

## QuerySets e consultas

Consultas reutilizáveis devem preferencialmente ficar em:

```text
QuerySet
Manager
Selector
Repository
```

conforme o padrão adotado pelo projeto.

Não duplicar consultas complexas em diferentes views.

---

## Validação

Nunca confiar exclusivamente em validações feitas no frontend.

Utilizar:

- Forms;
- ModelForms;
- Serializers;
- validações de domínio;
- constraints do PostgreSQL.

Sempre que possível, invariantes críticas devem também possuir proteção no banco.

---

# Banco de dados

PostgreSQL será considerado a fonte oficial de verdade para os dados persistentes do sistema.

---

## Migrations

Toda alteração de estrutura deve possuir migration do Django.

Não modificar manualmente tabelas de produção como forma normal de desenvolvimento.

---

## Integridade

Utilizar quando aplicável:

```text
NOT NULL
UNIQUE
CHECK
FOREIGN KEY
constraints
```

Regras importantes não devem depender somente da aplicação quando o banco puder garantir integridade.

---

## Transações

Operações que precisam ocorrer integralmente devem utilizar transações.

Exemplo:

```text
chamar senha
+
registrar histórico
+
atualizar atendimento
+
registrar auditoria
```

Essas alterações não devem ficar parcialmente aplicadas.

---

## Performance

Evitar N+1 queries.

Utilizar conscientemente:

```python
select_related()
prefetch_related()
```

Não realizar otimizações prematuras.

Criar índices quando houver necessidade real baseada nos filtros e consultas utilizados.

---

# Segurança

Segurança deve ser tratada como parte da arquitetura e não como etapa posterior.

---

## Autenticação

Nunca implementar armazenamento próprio de senha.

Utilizar o sistema de autenticação do Django.

---

## Segredos

Nunca armazenar no código:

```text
senhas
tokens
chaves de API
credenciais
segredos
```

Utilizar variáveis de ambiente.

Arquivos contendo segredos não devem ser versionados.

---

## Logs

Nunca registrar em logs:

- senha;
- token;
- CPF completo;
- dados clínicos desnecessários;
- informações sensíveis sem necessidade operacional.

---

## Autorização

Ocultar uma funcionalidade no frontend não representa segurança.

Toda permissão deve ser validada no backend.

Endpoints protegidos devem verificar:

```text
autenticação
+
autorização
```

Preferir o princípio:

```text
negado por padrão
```

e liberar explicitamente as permissões necessárias.

---

# Dados de saúde

Informações relacionadas a pacientes devem ser consideradas sensíveis por padrão.

Coletar somente dados necessários para funcionamento do sistema.

Evitar armazenamento sem finalidade definida.

---

## Auditoria

Operações importantes devem possuir rastreabilidade.

Sempre que relevante registrar:

```text
quem realizou
o que realizou
quando realizou
estado anterior
novo estado
```

Exemplos:

```text
alteração de cadastro
mudança de status
chamada de senha
cancelamento
finalização de atendimento
alteração de agenda
```

---

## Histórico

Dados operacionalmente relevantes não devem ser sobrescritos silenciosamente quando houver necessidade de rastreabilidade.

Quando necessário, utilizar:

```text
históricos
eventos
status
versões
logs de auditoria
```

---

# Domínios do sistema

As áreas do sistema devem permanecer separadas.

Estrutura sugerida:

```text
apps/
├── accounts/
├── patients/
├── professionals/
├── appointments/
├── reception/
├── queue/
├── attendance/
├── rooms/
├── notifications/
├── reports/
└── audit/
```

Os nomes podem evoluir conforme o projeto.

A separação de responsabilidade deve permanecer.

---

## Comunicação entre domínios

Um domínio não deve manipular diretamente detalhes internos de outro domínio quando existir uma interface pública apropriada.

Evitar:

```text
reception acessando e alterando diretamente vários models internos de queue
```

Preferir:

```text
reception
    ↓
queue.services.call_ticket()
```

Isso reduz acoplamento e facilita manutenção.

---

# API

Endpoints devem possuir comportamento previsível.

Preferir recursos claramente identificados.

Validar todos os dados de entrada.

---

## Erros de API

Respostas de erro devem seguir estrutura consistente.

Exemplo:

```json
{
  "error": {
    "code": "queue_ticket_not_found",
    "message": "A senha informada não foi encontrada."
  }
}
```

Não retornar stack traces ou exceções internas para clientes.

---

## Schemas

Modelos de banco e contratos de API não devem ser considerados automaticamente equivalentes.

A API deve possuir contratos explicitamente definidos.

---

# Frontend

Frontend deve ser responsável principalmente por:

- apresentação;
- interação;
- feedback visual;
- coleta de entrada do usuário.

Regras críticas de negócio permanecem no backend.

---

## Interface operacional

Telas utilizadas continuamente por:

```text
recepção
atendentes
médicos
profissionais
```

devem priorizar:

```text
clareza
velocidade
poucos cliques
feedback imediato
baixo esforço cognitivo
```

Evitar interfaces excessivamente decorativas em fluxos operacionais.

---

# Logging

Logs técnicos devem ser estruturados.

Preferir JSON quando utilizados para:

```text
debug
monitoramento
observabilidade
auditoria técnica
```

Exemplo:

```json
{
  "event": "queue_ticket_called",
  "ticket_id": 123,
  "room_id": 4
}
```

Saídas destinadas diretamente ao usuário podem utilizar texto comum.

---

# Formatação

Utilizar o formatador padrão da linguagem ou framework.

Exemplos:

```text
black
ruff format
prettier
gofmt
cargo fmt
```

Não criar discussões ou padrões próprios de formatação quando já existir ferramenta consolidada.

---

# Princípio geral

Antes de adicionar código, identificar:

1. a qual domínio pertence;
2. qual responsabilidade está sendo implementada;
3. se já existe implementação equivalente;
4. se existe convenção do framework para resolver o problema;
5. quais testes devem proteger o comportamento.

A prioridade deve ser:

```text
clareza
>
coesão
>
simplicidade
>
reutilização
>
abstração
```

Não criar arquitetura complexa para problemas simples.

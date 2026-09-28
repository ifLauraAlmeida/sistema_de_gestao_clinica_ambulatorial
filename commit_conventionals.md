# Convenção de commits

Este documento define obrigatoriamente o padrão de commits utilizado neste projeto.

Todos os commits devem seguir o padrão **Conventional Commits**.

Além do formato convencional, este projeto possui regras adicionais de idioma, escrita e separação de responsabilidades.

---

# Idioma

Todos os commits devem ser escritos integralmente em português.

Não utilizar descrições em inglês.

Evitar:

```text
feat: add patient screen
fix: update queue status
refactor: change appointment service
```

Utilizar:

```text
feat: adiciona tela de pacientes
fix: corrige atualização da fila
refactor: reorganiza serviço de agendamento
```

Os identificadores do Conventional Commits permanecem no formato padrão:

```text
feat
fix
refactor
test
docs
style
perf
build
ci
chore
revert
```

Porém, toda descrição deve estar em português.

---

# Letras minúsculas

A mensagem principal do commit deve ser escrita totalmente em letras minúsculas.

Correto:

```text
feat: adiciona chamada de senha
```

Incorreto:

```text
feat: Adiciona chamada de senha
```

Incorreto:

```text
feat: ADICIONA CHAMADA DE SENHA
```

---

# Formato obrigatório

Utilizar:

```text
tipo: descrição
```

Quando houver escopo:

```text
tipo(escopo): descrição
```

Exemplos:

```text
feat(fila): adiciona chamada de senha
fix(agenda): corrige conflito entre horários
refactor(pacientes): separa validação de cadastro
test(fila): adiciona teste para rechamada de senha
docs: atualiza instruções de instalação
```

---

# Tipos de commit

## feat

Utilizado para novas funcionalidades.

Exemplos:

```text
feat(fila): adiciona chamada de senha
feat(pacientes): adiciona cadastro de paciente
feat(recepcao): adiciona painel de chegada
```

## fix

Utilizado para correções de comportamento incorreto.

Exemplos:

```text
fix(fila): corrige ordem das senhas prioritárias
fix(login): corrige redirecionamento após autenticação
```

## refactor

Utilizado quando o código é reorganizado sem alterar o comportamento esperado.

Exemplos:

```text
refactor(fila): separa regras de chamada em serviço
refactor(agenda): extrai consulta de disponibilidade
```

## test

Utilizado para criação ou alteração exclusiva de testes.

Exemplos:

```text
test(fila): adiciona testes de chamada de senha
test(pacientes): adiciona teste de cpf duplicado
```

## docs

Utilizado para documentação.

Exemplos:

```text
docs: atualiza readme
docs: documenta configuração do postgres
```

## style

Utilizado exclusivamente para alterações que não modificam comportamento.

Exemplos:

```text
style: aplica formatação automática
style(frontend): ajusta indentação dos templates
```

Não utilizar `style` para mudanças visuais de interface que alterem o produto.

Alterações reais de interface normalmente devem utilizar `feat` ou `fix`.

## perf

Utilizado para melhorias de desempenho.

Exemplos:

```text
perf(fila): reduz consultas ao buscar próximas senhas
perf(pacientes): adiciona prefetch aos atendimentos
```

## build

Utilizado para alterações relacionadas ao processo de build ou dependências.

Exemplos:

```text
build: adiciona dependência do postgres
build: atualiza versão do django
```

## ci

Utilizado para integração contínua.

Exemplos:

```text
ci: adiciona execução de testes no github actions
ci: adiciona verificação de formatação
```

## chore

Utilizado para tarefas de manutenção que não representam funcionalidade.

Exemplos:

```text
chore: atualiza gitignore
chore: remove arquivos temporários
```

Evitar utilizar `chore` como categoria genérica para qualquer alteração.

## revert

Utilizado para desfazer um commit anterior.

Exemplo:

```text
revert: desfaz alteração da fila prioritária
```

---

# Escopos

Escopos devem representar uma área clara do sistema.

Exemplos recomendados:

```text
auth
usuarios
pacientes
profissionais
agenda
recepcao
fila
atendimento
salas
notificacoes
relatorios
auditoria
api
frontend
infra
```

Não criar escopos excessivamente genéricos.

Evitar:

```text
core
misc
geral
codigo
sistema
```

quando existir um domínio mais específico.

---

# Separação dos commits

Commits devem representar uma única alteração lógica.

Uma funcionalidade deve ser comitada separadamente de outra funcionalidade independente.

## Regra principal

Evitar ao máximo colocar arquivos de funções ou responsabilidades diferentes dentro do mesmo commit.

Por exemplo, se forem realizadas as seguintes alterações:

```text
criação da chamada de senha
correção da agenda
alteração visual do login
```

devem ser criados três commits independentes.

Exemplo:

```text
feat(fila): adiciona chamada de senha
fix(agenda): corrige conflito de horários
style(auth): ajusta espaçamento da tela de login
```

---

# Arquivos relacionados

É permitido incluir múltiplos arquivos no mesmo commit quando todos fizerem parte da mesma alteração lógica.

Exemplo:

```text
queue/models.py
queue/services/call_ticket.py
queue/tests/test_call_ticket.py
```

podem fazer parte de:

```text
feat(fila): adiciona chamada de senha
```

porque todos pertencem à mesma funcionalidade.

---

# Arquivos não relacionados

Evitar:

```text
git add .
git commit -m "feat: atualiza sistema"
```

quando o diretório contém alterações independentes.

Antes de criar um commit, revisar:

```bash
git status
```

e:

```bash
git diff
```

Adicionar apenas arquivos relacionados ao objetivo daquele commit.

Exemplo:

```bash
git add apps/queue/models.py
git add apps/queue/services/call_ticket.py
git add apps/queue/tests/test_call_ticket.py
```

Depois:

```bash
git commit -m "feat(fila): adiciona chamada de senha"
```

---

# Alterações parciais

Quando um arquivo possuir mudanças relacionadas a mais de uma funcionalidade, utilizar staging parcial.

Exemplo:

```bash
git add -p
```

Isso permite selecionar somente os trechos que pertencem ao commit atual.

---

# Granularidade

Preferir:

```text
1 responsabilidade
=
1 commit
```

Um commit deve conseguir responder claramente:

```text
qual mudança específica este commit introduz?
```

Se a resposta exigir mencionar várias funcionalidades independentes, o commit provavelmente deve ser dividido.

---

# Exemplos corretos

```text
feat(pacientes): adiciona cadastro de paciente
feat(fila): adiciona geração de senha
feat(fila): adiciona chamada de senha
feat(fila): adiciona rechamada de senha
fix(fila): impede chamada de senha finalizada
feat(atendimento): adiciona início de consulta
feat(atendimento): adiciona encerramento de consulta
test(atendimento): adiciona testes de encerramento
docs: documenta execução local
chore: atualiza gitignore
```

---

# Exemplos incorretos

Evitar:

```text
feat: várias alterações
```

Evitar:

```text
feat: finaliza sistema
```

Evitar:

```text
fix: corrige coisas
```

Evitar:

```text
update project
```

Evitar:

```text
feat: adiciona pacientes, corrige fila e muda login
```

Evitar:

```text
feat: Ajusta Sistema
```

---

# Descrição dos commits

As mensagens devem ser:

- objetivas;
- específicas;
- escritas em português;
- escritas em minúsculo;
- relacionadas diretamente à alteração realizada.

Preferir verbo no presente:

```text
adiciona
corrige
remove
atualiza
separa
simplifica
impede
permite
cria
ajusta
```

---

# Commits atômicos

Commits devem ser atômicos.

Isso significa que cada commit deve representar uma alteração completa e coerente que possa, idealmente:

```text
ser analisada isoladamente
ser revertida isoladamente
ser testada isoladamente
```

Um commit não deve depender de alterações não relacionadas incluídas apenas por conveniência.

---

# Testes e funcionalidade

Quando um teste for criado especificamente para uma nova funcionalidade, ele pode fazer parte do mesmo commit da funcionalidade.

Exemplo:

```text
feat(fila): adiciona chamada de senha
```

pode conter:

```text
call_ticket.py
test_call_ticket.py
```

Quando a alteração for exclusivamente em testes existentes, utilizar:

```text
test(...)
```

---

# Refatoração e funcionalidade

Sempre que possível, separar refatorações de novas funcionalidades.

Preferir:

```text
refactor(fila): separa serviço de chamada
```

seguido por:

```text
feat(fila): adiciona rechamada automática
```

em vez de:

```text
feat(fila): refatora fila e adiciona rechamada
```

Isso facilita:

- revisão;
- rollback;
- identificação de bugs;
- análise do histórico.

---

# Correções

Uma correção deve conter somente alterações necessárias para corrigir aquele problema e seus testes associados.

Evitar utilizar um `fix` como oportunidade para reorganizar partes não relacionadas do código.

---

# Antes de cada commit

Antes de criar um commit:

1. executar `git status`;
2. revisar `git diff`;
3. identificar qual alteração lógica será comitada;
4. adicionar somente arquivos relacionados;
5. executar testes aplicáveis;
6. criar a mensagem no padrão definido neste documento.

---

# Regra para agentes de IA

Agentes de IA não devem utilizar automaticamente:

```bash
git add .
```

ou:

```bash
git add -A
```

sem antes verificar se todas as alterações pertencem à mesma responsabilidade.

O agente deve:

1. analisar os arquivos modificados;
2. agrupar alterações por responsabilidade;
3. criar commits independentes;
4. utilizar mensagens em português;
5. utilizar somente letras minúsculas na mensagem;
6. seguir Conventional Commits;
7. evitar misturar funcionalidades independentes;
8. incluir os testes da funcionalidade no mesmo commit quando apropriado;
9. separar refatorações de funcionalidades sempre que possível.

---

# Regra final

O histórico Git deve contar a evolução do sistema de forma compreensível.

Preferir:

```text
feat(pacientes): adiciona cadastro de paciente
feat(fila): adiciona geração de senha
feat(fila): adiciona chamada de senha
fix(fila): corrige prioridade no atendimento
feat(atendimento): adiciona finalização de consulta
```

em vez de:

```text
feat: sistema funcionando
```

Cada commit deve representar uma única decisão técnica ou funcional identificável.

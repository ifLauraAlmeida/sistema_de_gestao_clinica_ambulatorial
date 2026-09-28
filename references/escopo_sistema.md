# Escopo do Sistema de Gestão Clínica Ambulatorial

## 1. Visão geral

O **Sistema de Gestão Clínica Ambulatorial (SGCA)** é uma aplicação web destinada à digitalização e organização de fluxos administrativos e assistenciais de clínicas, centros médicos e serviços ambulatoriais.

O sistema deverá centralizar cadastro de pacientes, agenda, check-in, filas, chamadas, prontuário eletrônico, documentos clínicos, autorizações, pagamentos, auditoria e indicadores operacionais, reduzindo dependência de papel, retrabalho e processos manuais.

A solução deverá funcionar através de navegador, com interface em HTML, podendo ser hospedada:

- em infraestrutura local da clínica;
- em servidor local com acesso pela rede interna;
- em VPS/cloud;
- ou em arquitetura híbrida, dependendo do orçamento, disponibilidade de internet, necessidade de acesso remoto e requisitos de segurança.

O objetivo inicial não é criar um sistema hospitalar extremamente complexo, mas um sistema **simples, rápido, confiável e adaptado ao fluxo real da clínica**.

---

# 2. Problema atual

O fluxo atualmente observado apresenta forte dependência de documentos físicos e processos manuais.

Entre os principais pontos identificados:

- existência de poucos computadores;
- separação física entre recepção de marcação, recepção de chegada e recepção financeira;
- uso de senhas/fila por especialidade;
- necessidade de localizar fichas físicas;
- criação de nova ficha quando o cadastro não é localizado;
- existência operacional de "arquivo vivo" e "arquivo morto";
- circulação da mesma ficha física entre diferentes especialidades;
- risco de perda, duplicação ou preenchimento incorreto de fichas;
- demora na localização de prontuários;
- possibilidade de pacientes serem atendidos fora da ordem real da fila devido a atrasos administrativos;
- dificuldade para gerar indicadores de gestão;
- dificuldade para consultar histórico de atendimento;
- ausência de rastreabilidade detalhada sobre alterações em registros;
- dependência de documentos físicos para informações clínicas;
- dificuldade de compartilhamento controlado de informações entre setores;
- aumento de carga de trabalho da recepção.

---

# 3. Objetivos do projeto

## 3.1 Objetivo principal

Digitalizar o fluxo assistencial e administrativo da clínica, reduzindo tempo de atendimento, retrabalho, circulação de documentos físicos e dependência de arquivos manuais.

## 3.2 Objetivos específicos

- Criar cadastro único de pacientes.
- Eliminar a lógica operacional de arquivo vivo e arquivo morto.
- Manter histórico permanente de atendimentos.
- Criar controle eletrônico de filas.
- Separar filas por especialidade e profissional.
- Organizar fluxo de chegada, autorização/pagamento e atendimento médico.
- Permitir acesso ao prontuário de acordo com perfil e necessidade.
- Restringir médicos aos pacientes relacionados à sua agenda/fila.
- Digitalizar registros clínicos.
- Permitir emissão de documentos médicos.
- Permitir assinatura eletrônica dos documentos.
- Registrar todo acesso relevante a informações clínicas.
- Criar histórico de alterações.
- Permitir geração de relatórios administrativos.
- Gerar indicadores de produtividade e operação.
- Reduzir o tempo gasto procurando fichas físicas.
- Evitar criação de cadastros duplicados.
- Permitir crescimento futuro sem reconstrução completa do sistema.

---

# 4. Princípios do sistema

O sistema deverá ser desenvolvido seguindo os seguintes princípios:

1. **Simplicidade operacional**  
   A interface deve exigir pouca curva de aprendizado.

2. **Velocidade**  
   Operações comuns de recepção devem exigir poucos cliques.

3. **Controle por perfil**  
   Cada usuário verá apenas o necessário para executar sua função.

4. **Rastreabilidade**  
   Ações relevantes deverão ser registradas.

5. **Privacidade**  
   Dados clínicos não devem ficar acessíveis a funcionários sem necessidade funcional.

6. **Cadastro único do paciente**  
   Um paciente deve possuir apenas um cadastro principal.

7. **Histórico permanente**  
   O sistema não deverá eliminar cadastros por ausência de atendimento.

8. **Fila como evento operacional**  
   A fila deverá representar o percurso real do paciente dentro da clínica.

9. **Escalabilidade gradual**  
   O sistema deverá permitir inclusão futura de novos módulos.

10. **Baixa dependência de papel**  
    Sempre que juridicamente e operacionalmente possível, documentos deverão ser digitais.

---

# 5. Perfis de usuário

## 5.1 Administrador do sistema

Responsável por configuração e gestão técnica/administrativa.

### Acesso

- cadastro de usuários;
- ativação e desativação de usuários;
- definição de perfis e permissões;
- cadastro de especialidades;
- cadastro de profissionais;
- configuração de horários;
- configuração de convênios;
- configuração de tipos de atendimento;
- visualização de logs;
- relatórios gerais;
- parametrização do sistema.

O administrador técnico **não deverá necessariamente possuir acesso irrestrito ao conteúdo clínico**.

---

## 5.2 Recepção de marcação

Responsável por agendamentos.

### Acesso

- localizar paciente;
- cadastrar novo paciente;
- atualizar dados cadastrais;
- consultar agenda;
- criar agendamento;
- remarcar;
- cancelar;
- consultar disponibilidade;
- visualizar especialidade;
- visualizar profissional;
- consultar situação administrativa do agendamento.

### Sem acesso

- evolução médica;
- diagnóstico detalhado;
- documentos clínicos não necessários à atividade;
- registros clínicos confidenciais.

---

## 5.3 Recepção de chegada / atendimento

Responsável pelo check-in do paciente.

### Acesso

- localizar paciente;
- confirmar chegada;
- confirmar especialidade;
- confirmar profissional;
- inserir paciente na fila correspondente;
- visualizar posição administrativa na fila;
- atualizar dados cadastrais básicos;
- registrar observações administrativas;
- direcionar paciente para outro setor.

---

## 5.4 Recepção financeira / autorização

Responsável por pagamento, convênio, autorização e comandas.

### Acesso

- consultar atendimento do dia;
- consultar convênio;
- registrar autorização;
- registrar número de guia;
- registrar forma de pagamento;
- registrar valor;
- confirmar liberação administrativa do atendimento;
- emitir comprovantes;
- visualizar pendências administrativas.

### Sem acesso

- evolução clínica;
- diagnóstico clínico detalhado;
- anotações médicas desnecessárias ao faturamento.

---

## 5.5 Médico / profissional assistencial

### Acesso

O profissional deverá visualizar prioritariamente:

- pacientes da sua agenda do dia;
- pacientes inseridos em sua fila;
- histórico clínico dos pacientes sob seu atendimento;
- atendimentos anteriores daquele paciente;
- documentos médicos relacionados;
- exames anexados, caso o módulo exista;
- alergias;
- medicamentos registrados;
- informações relevantes ao cuidado.

### Funcionalidades

- chamar próximo paciente;
- iniciar atendimento;
- registrar evolução;
- registrar hipótese diagnóstica;
- registrar diagnóstico;
- registrar conduta;
- criar prescrição;
- emitir relatório;
- emitir atestado;
- emitir declaração;
- solicitar exames;
- gerar encaminhamento;
- assinar documentos;
- finalizar atendimento.

### Restrição

O profissional não deverá possuir mecanismo de consulta indiscriminada ao prontuário de qualquer paciente da clínica sem justificativa funcional.

---

## 5.6 Enfermagem / apoio assistencial

Caso utilizado futuramente.

### Possíveis acessos

- triagem;
- pressão arterial;
- peso;
- altura;
- temperatura;
- glicemia;
- saturação;
- frequência cardíaca;
- informações de risco;
- encaminhamento para fila médica.

---

## 5.7 Gestão / direção

### Acesso

- indicadores;
- produtividade;
- quantidade de atendimentos;
- tempo médio de espera;
- volume por especialidade;
- volume por profissional;
- cancelamentos;
- faltas;
- pagamentos;
- convênios;
- autorizações;
- desempenho operacional;
- relatórios agregados.

O acesso a informações clínicas individualizadas deverá ser limitado.

---

# 6. Controle de permissões

O sistema deverá utilizar **RBAC — Role-Based Access Control**, ou controle de acesso baseado em função.

Exemplos de permissões:

- `paciente.visualizar`
- `paciente.criar`
- `paciente.editar`
- `agenda.visualizar`
- `agenda.criar`
- `fila.visualizar`
- `fila.gerenciar`
- `financeiro.visualizar`
- `financeiro.editar`
- `prontuario.visualizar`
- `prontuario.editar`
- `documento.assinar`
- `relatorio.visualizar`
- `usuario.gerenciar`

Isso permitirá alterar permissões posteriormente sem reescrever o sistema.

---

# 7. Cadastro único de pacientes

Cada paciente deverá possuir um identificador interno único.

## 7.1 Dados básicos

Exemplos:

- ID interno;
- nome completo;
- nome social, quando aplicável;
- CPF;
- CNS, caso utilizado;
- data de nascimento;
- sexo;
- telefone;
- WhatsApp;
- e-mail;
- endereço;
- bairro;
- município;
- CEP;
- nome da mãe;
- contato de emergência;
- convênio;
- número da carteirinha;
- validade;
- observações administrativas.

---

# 8. Prevenção de duplicidades

Antes de criar um paciente, o sistema deverá pesquisar possíveis correspondências.

Critérios possíveis:

- CPF;
- CNS;
- nome + data de nascimento;
- nome + nome da mãe;
- telefone.

Ao encontrar possível duplicidade, deverá alertar:

> "Já existe um paciente com dados semelhantes."

A criação de outro cadastro deverá exigir confirmação de usuário autorizado.

---

# 9. Histórico do paciente

O cadastro não deverá ser movido para "arquivo morto".

Pacientes sem atendimento por vários anos continuarão disponíveis no banco.

O sistema poderá indicar:

- última consulta;
- última especialidade;
- número total de atendimentos;
- status cadastral;
- data da última atualização.

O conceito de "arquivo morto" poderá existir apenas para **documentos físicos legados**, caso a clínica decida mantê-los durante a transição.

---

# 10. Fluxo geral do paciente

Fluxo proposto:

```text
AGENDAMENTO
    ↓
CHEGADA À CLÍNICA
    ↓
IDENTIFICAÇÃO DO PACIENTE
    ↓
CHECK-IN
    ↓
FILA ADMINISTRATIVA / AUTORIZAÇÃO
    ↓
PAGAMENTO OU CONVÊNIO
    ↓
LIBERAÇÃO DO ATENDIMENTO
    ↓
FILA DO PROFISSIONAL
    ↓
CHAMADA
    ↓
ATENDIMENTO
    ↓
DOCUMENTOS / PRESCRIÇÕES
    ↓
FINALIZAÇÃO
```

O fluxo deverá ser configurável de acordo com o tipo de atendimento.

---

# 11. Sistema de filas

Este deverá ser um dos principais módulos.

## 11.1 Tipos de fila

Poderão existir:

- fila de recepção;
- fila de autorização;
- fila financeira;
- fila por especialidade;
- fila por profissional;
- fila de procedimento;
- fila de retorno.

---

# 12. Estados de um atendimento

Sugestão:

```text
AGENDADO
CHECK_IN_REALIZADO
AGUARDANDO_AUTORIZACAO
AGUARDANDO_PAGAMENTO
LIBERADO
AGUARDANDO_PROFISSIONAL
CHAMADO
EM_ATENDIMENTO
FINALIZADO
CANCELADO
NAO_COMPARECEU
```

Cada mudança deverá possuir:

- data;
- hora;
- usuário responsável;
- setor;
- status anterior;
- status novo.

---

# 13. Ordem da fila

A fila deverá considerar inicialmente a ordem de entrada.

Entretanto, deverá suportar regras como:

- prioridade legal;
- prioridade clínica;
- encaixe;
- retorno;
- emergência;
- paciente previamente chamado;
- atendimento preferencial.

Mudanças manuais na ordem deverão ser registradas em log.

---

# 14. Painel da recepção

A recepção poderá visualizar algo semelhante a:

| Senha | Paciente | Especialidade | Profissional | Status | Espera |
|---|---|---|---|---|---|
| C012 | Maria S. | Cardiologia | Dr. X | Aguardando | 18 min |
| O004 | João P. | Ortopedia | Dra. Y | Liberado | 11 min |

O nome completo poderá ser ocultado em telas públicas.

---

# 15. Painel público de chamadas e integração em tempo real

O sistema deverá possuir um módulo específico para **chamada de senhas em tempo real**, integrado às filas administrativas e assistenciais.

A proposta é que o painel público seja uma página do próprio sistema web, aberta em navegador e exibida em televisão, monitor ou equipamento dedicado.

Exemplo de rota:

```text
/painel
```

ou, caso existam painéis separados:

```text
/painel/recepcao
/painel/consultorios
/painel/andar-1
/painel/andar-2
```

A página poderá permanecer aberta em modo tela cheia ou modo kiosk.

## 15.1 Fluxo de uma chamada

Exemplo:

```text
RECEPÇÃO / PROFISSIONAL
        ↓
clica em CHAMAR
        ↓
BACKEND
        ↓
registra a chamada no banco
        ↓
publica evento em tempo real
        ↓
PAINEL PÚBLICO
        ↓
exibe senha + destino
```

Exemplo de chamada:

```text
GINE01

CONSULTÓRIO 04
```

Outro exemplo:

```text
ORTO04

RECEPÇÃO
GUICHÊ 01
```

O painel não deverá depender de atualização manual da página.

---

## 15.2 Senha e destino devem ser entidades separadas

A senha representa o paciente dentro do fluxo daquele atendimento.

Exemplo:

```text
ORTO04
```

O destino representa para onde ele está sendo chamado naquele momento.

Exemplo:

```text
ORTO04
→ RECEPÇÃO / GUICHÊ 01
```

Posteriormente, a mesma senha poderá ser chamada novamente:

```text
ORTO04
→ CONSULTÓRIO 07
```

Portanto, não se recomenda incorporar permanentemente o guichê ou consultório ao código da senha.

Isso permite que a mesma senha percorra diferentes etapas da clínica.

---

## 15.3 Geração das senhas

As senhas poderão possuir prefixos definidos por especialidade ou tipo de fluxo.

Exemplos:

```text
GINE01
GINE02

ORTO01
ORTO02

CARD01
CARD02
```

Os prefixos deverão ser configuráveis no sistema.

Também poderá existir numeração administrativa independente da especialidade, caso o fluxo real da clínica demonstre essa necessidade.

---

## 15.4 Chamada pelo funcionário

Na recepção, o funcionário poderá visualizar algo semelhante a:

```text
ORTO04
Paciente aguardando

[ CHAMAR PARA GUICHÊ 01 ]
```

O profissional assistencial poderá visualizar:

```text
MINHA FILA

GINE01   aguardando há 08 min
GINE02   aguardando há 04 min
GINE03   aguardando há 01 min
```

Ações disponíveis:

```text
[ CHAMAR ]
[ RECHAMAR ]
[ INICIAR ATENDIMENTO ]
[ NÃO COMPARECEU ]
```

Ao chamar:

```text
Destino:
[ Consultório 04 ▼ ]

[ CONFIRMAR CHAMADA ]
```

---

## 15.5 Comunicação com a tela

A tela pública deverá receber as chamadas diretamente do backend.

Existem três estratégias possíveis.

### Polling

O navegador consulta periodicamente o servidor:

```text
painel → servidor
"existe uma nova chamada?"
```

Exemplo:

```text
a cada 2 ou 3 segundos
```

É simples de implementar, porém gera requisições repetidas mesmo quando nada mudou.

### Server-Sent Events — SSE

O navegador mantém uma conexão com o servidor e recebe novos eventos conforme forem publicados.

Fluxo:

```text
SERVIDOR → PAINEL
```

É adequado quando a comunicação é predominantemente unidirecional.

### WebSocket

Mantém uma conexão persistente entre navegador e servidor.

```text
SERVIDOR ↔ NAVEGADOR
```

É a opção recomendada caso o sistema utilize atualização em tempo real também nas filas internas de médicos e recepções.

---

## 15.6 Arquitetura recomendada para tempo real

Para a stack Django, uma arquitetura possível é:

```text
Django
+
Django Channels
+
WebSocket
+
Redis
+
PostgreSQL
```

Fluxo simplificado:

```text
FUNCIONÁRIO CHAMA ORTO04
          ↓
       Django
          ↓
 registra no PostgreSQL
          ↓
 publica evento
          ↓
        Redis
          ↓
      WebSocket
          ↓
   PAINEL / TV RECEBE
```

Arquitetura conceitual:

```text
                   ┌─────────────────────┐
                   │     PostgreSQL      │
                   └─────────▲───────────┘
                             │
                    ┌────────┴────────┐
                    │     Django      │
                    │     Backend     │
                    └────────┬────────┘
                             │
                    WebSocket / SSE
                             │
       ┌─────────────────────┼──────────────────────┐
       │                     │                      │
       ▼                     ▼                      ▼
 Recepção 1              Recepção 2            TV / Painel
 navegador               navegador              navegador
```

O Redis poderá atuar como camada de distribuição de eventos quando necessário.

Para instalações pequenas, a arquitetura deverá ser dimensionada para evitar complexidade desnecessária.

---

## 15.7 Registro da chamada

A fila e a chamada não deverão ser tratadas como a mesma informação.

Uma fila representa:

```text
senha: ORTO04
posição: 4
status: aguardando
```

Uma chamada representa um evento:

```text
senha: ORTO04
horário: 10:42:17
destino: RECEPÇÃO
guichê: 01
```

Uma possível tabela:

```text
chamadas
```

Campos conceituais:

```text
id
atendimento_id
fila_id
senha
tipo_destino
destino_id
destino_texto
painel_destino
chamado_por
data_hora
numero_tentativa
status
```

---

## 15.8 Histórico de chamadas

O sistema deverá manter histórico.

Exemplo:

```text
10:42:17 — ORTO04 chamado para RECEPÇÃO / GUICHÊ 01
10:43:28 — ORTO04 rechamado
10:45:03 — atendimento iniciado
```

Isso permitirá calcular posteriormente:

- tempo entre chamada e atendimento;
- quantidade de rechamadas;
- pacientes que não responderam à chamada;
- tempo de permanência em cada etapa;
- gargalos por guichê;
- gargalos por especialidade.

---

## 15.9 Exibição no painel público

Sugestão de organização:

```text
┌─────────────────────────────────────────┐
│                                         │
│               GINE01                    │
│                                         │
│           CONSULTÓRIO 04                │
│                                         │
├─────────────────────────────────────────┤
│ ÚLTIMAS CHAMADAS                        │
│                                         │
│ ORTO04       RECEPÇÃO — GUICHÊ 01       │
│ CARD03       CONSULTÓRIO 07              │
│ GINE08       CONSULTÓRIO 04              │
└─────────────────────────────────────────┘
```

O painel deverá destacar visualmente a chamada mais recente.

---

## 15.10 Privacidade no painel

O painel público não deverá exibir dados pessoais desnecessários.

Preferencialmente:

```text
GINE01
CONSULTÓRIO 04
```

e não:

```text
Maria da Silva
CONSULTÓRIO 04
```

A utilização de nomes deverá ser evitada para reduzir exposição de informações pessoais.

---

## 15.11 Sinal sonoro

Ao receber nova chamada, o painel poderá emitir:

```text
♪ aviso sonoro
```

seguido da exibição visual.

O volume deverá ser configurável de acordo com o ambiente.

---

## 15.12 Síntese de voz

Opcionalmente, o painel poderá anunciar:

> "Senha GINE zero um. Dirija-se ao consultório quatro."

A funcionalidade poderá utilizar:

- síntese de voz do navegador/sistema operacional;
- biblioteca local;
- serviço externo de Text-to-Speech.

A solução deverá priorizar funcionamento simples e baixo custo.

---

## 15.13 Rechamada

O sistema deverá permitir rechamar uma senha sem gerar um novo atendimento.

Exemplo:

```text
[ RECHAMAR GINE01 ]
```

Cada rechamada deverá ser registrada como novo evento vinculado à mesma fila.

---

## 15.14 Não comparecimento à chamada

Caso o paciente não responda:

```text
[ NÃO RESPONDEU À CHAMADA ]
```

O sistema poderá:

- manter o paciente aguardando;
- mover temporariamente sua posição;
- registrar tentativa;
- permitir rechamada;
- marcar como ausente após regra configurada.

A regra deverá ser definida conforme o processo da clínica.

---

## 15.15 Múltiplos painéis

A arquitetura deverá permitir diferentes telas para diferentes áreas.

Exemplo:

```text
PAINEL_RECEPCAO
```

recebe chamadas de:

- marcação;
- autorização;
- financeiro;
- recepção.

Enquanto:

```text
PAINEL_CONSULTORIOS
```

recebe chamadas de:

- ginecologia;
- ortopedia;
- cardiologia;
- outras especialidades.

Cada chamada poderá conter:

```text
painel_destino
```

Exemplo:

```text
GINE01
painel_destino = CONSULTORIOS
```

```text
ORTO04
painel_destino = RECEPCAO
```

Assim, cada televisão recebe apenas os eventos relevantes àquela área.

---

## 15.16 Operação em televisão ou monitor

Não deverá ser necessário instalar um aplicativo dedicado.

O painel poderá funcionar em:

- computador;
- mini PC;
- Raspberry Pi;
- dispositivo compatível com navegador;
- Smart TV com navegador adequado, caso tecnicamente estável.

O navegador deverá permanecer aberto em uma URL do sistema, por exemplo:

```text
https://sistema.clinica.local/painel/recepcao
```

ou equivalente em infraestrutura cloud.

Preferencialmente em:

```text
modo kiosk / tela cheia
```

---

## 15.17 Recuperação de conexão

Caso a conexão em tempo real seja interrompida, o painel deverá:

1. detectar a desconexão;
2. tentar reconectar automaticamente;
3. consultar a última chamada válida;
4. continuar a operação sem exigir intervenção manual.

O painel também deverá possuir indicação discreta de estado:

```text
● conectado
```

ou:

```text
○ reconectando
```

---

## 15.18 Segurança do painel

O painel público deverá possuir acesso estritamente limitado.

Ele poderá receber apenas informações necessárias à exibição:

```text
senha
destino
horário
```

Não deverá receber:

- CPF;
- prontuário;
- diagnóstico;
- telefone;
- dados de pagamento;
- informações clínicas.

---

## 15.19 Atualização das filas internas

A mesma infraestrutura em tempo real poderá atualizar automaticamente:

- fila da recepção;
- fila do financeiro;
- fila do médico;
- fila de procedimentos;
- painel gerencial.

Exemplo:

```text
recepção realiza check-in
        ↓
fila do médico recebe o paciente
        ↓
tela do médico atualiza automaticamente
```

Sem necessidade de:

```text
F5
```

ou atualização manual.

---

## 15.20 Requisitos do módulo de chamadas

O módulo deverá contemplar:

- geração de senha;
- prefixos configuráveis;
- chamada;
- rechamada;
- destino;
- guichê;
- consultório;
- histórico de chamadas;
- registro de tentativas;
- chamada em tempo real;
- múltiplos painéis;
- últimas chamadas;
- aviso sonoro;
- síntese de voz opcional;
- anonimização;
- modo tela cheia;
- reconexão automática;
- logs;
- integração direta com as filas;
- atualização em tempo real das telas internas.

---


# 16. Agenda médica

O sistema deverá permitir:

- criar grade de atendimento;
- definir dias da semana;
- horário inicial;
- horário final;
- duração padrão;
- intervalos;
- bloqueios;
- férias;
- ausência;
- encaixes;
- limite de pacientes;
- retorno.

---

# 17. Check-in

Ao chegar, o paciente poderá ser localizado por:

- CPF;
- nome;
- data de nascimento;
- telefone;
- número de agendamento.

A recepção confirma sua presença e o sistema registra automaticamente horário de chegada.

---

# 18. Prontuário eletrônico

O prontuário deverá centralizar os registros clínicos.

## 18.1 Resumo do paciente

Ao abrir o atendimento:

```text
Paciente: Maria da Silva
Idade: 42 anos
Alergias: Dipirona
Última consulta: 15/08/2026
Especialidade atual: Cardiologia
```

---

# 19. Estrutura básica do atendimento médico

Possíveis campos:

- motivo da consulta;
- queixa principal;
- história da doença atual;
- antecedentes;
- alergias;
- medicamentos em uso;
- exame físico;
- hipótese diagnóstica;
- diagnóstico;
- CID;
- conduta;
- observações;
- retorno recomendado.

A estrutura deverá permitir campos livres e campos estruturados.

---

# 20. Linha do tempo clínica

Cada paciente deverá possuir uma timeline:

```text
27/09/2026 — Cardiologia
10/06/2026 — Clínica médica
05/01/2026 — Ortopedia
18/11/2025 — Cardiologia
```

Ao selecionar um atendimento, o profissional autorizado poderá consultar o registro correspondente.

---

# 21. Documentos médicos

O sistema poderá gerar:

- receita;
- atestado;
- declaração de comparecimento;
- relatório médico;
- encaminhamento;
- solicitação de exame;
- pedido de procedimento;
- laudo;
- documento personalizado.

Todos deverão possuir modelo padronizado.

---

# 22. Assinatura eletrônica

O sistema deverá prever assinatura eletrônica dos documentos médicos.

Possíveis modelos:

## Nível 1 — assinatura eletrônica interna

- usuário autenticado;
- senha;
- registro de data/hora;
- identificação do profissional;
- hash do documento;
- log de assinatura.

## Nível 2 — assinatura digital

Integração futura com certificado digital.

Exemplos:

- certificado A1;
- certificado A3;
- ICP-Brasil;
- serviços externos de assinatura.

A modalidade definitiva deverá ser validada conforme o tipo de documento, exigências regulatórias e jurídico da clínica.

---

# 23. Imutabilidade de documentos assinados

Após assinatura:

- o documento não poderá ser sobrescrito;
- correções deverão gerar nova versão;
- versão anterior deverá permanecer registrada;
- deverá existir data/hora;
- autor;
- motivo da correção.

---

# 24. Financeiro e convênios

O sistema poderá registrar:

- atendimento particular;
- convênio;
- plano;
- número da carteirinha;
- autorização;
- número de guia;
- valor da consulta;
- forma de pagamento;
- status do pagamento;
- desconto;
- isenção;
- responsável pelo lançamento.

---

# 25. Comandas de serviço

A comanda poderá passar a existir digitalmente.

Campos:

- paciente;
- data;
- profissional;
- especialidade;
- procedimento;
- convênio;
- código;
- valor;
- autorização;
- situação;
- responsável pela conferência.

Posteriormente poderá ser integrada ao faturamento.

---

# 26. Relatórios administrativos

## Operacionais

- pacientes atendidos por dia;
- pacientes por especialidade;
- pacientes por profissional;
- tempo médio de espera;
- tempo médio entre check-in e atendimento;
- faltas;
- cancelamentos;
- encaixes;
- quantidade de retornos;
- volume por horário;
- volume por dia da semana.

## Financeiros

- atendimentos particulares;
- valor recebido;
- forma de pagamento;
- atendimentos por convênio;
- volume por operadora;
- pendências de autorização.

---

# 27. Indicadores

Exemplos:

### Tempo médio de espera

```text
início do atendimento - horário de check-in
```

### Tempo administrativo

```text
liberação - horário de check-in
```

### Tempo aguardando profissional

```text
chamada - horário de liberação
```

### Taxa de falta

```text
não compareceu / total agendado
```

### Taxa de ocupação da agenda

```text
horários utilizados / horários disponíveis
```

---

# 28. Dashboard gerencial

Cards possíveis:

```text
Pacientes hoje
284

Tempo médio de espera
31 min

Em atendimento
18

Aguardando médico
52

Faltas
17

Atendimentos particulares
63
```

---

# 29. Auditoria

Toda operação relevante deverá possuir log.

Exemplos:

- login;
- logout;
- consulta a prontuário;
- criação de paciente;
- edição de paciente;
- abertura de prontuário;
- criação de documento;
- assinatura;
- alteração de fila;
- cancelamento;
- exclusão lógica;
- alteração de permissão.

---

# 30. Estrutura de log

Exemplo:

```text
usuario_id
acao
entidade
entidade_id
data_hora
ip
estacao
valor_anterior
valor_novo
```

Logs não devem ser alteráveis por usuários comuns.

---

# 31. LGPD e privacidade

Por tratar dados pessoais e dados de saúde, o sistema deverá ser projetado considerando a LGPD.

Medidas importantes:

- acesso mínimo necessário;
- perfis e permissões;
- autenticação individual;
- registro de acessos;
- criptografia;
- backup;
- política de retenção;
- restrição de exportação;
- timeout de sessão;
- bloqueio por tentativas de senha;
- logs;
- treinamento dos usuários;
- política de uso do sistema.

---

# 32. Segurança

## Requisitos mínimos

- HTTPS quando houver tráfego em rede;
- senhas armazenadas com hash seguro;
- nunca armazenar senha em texto puro;
- sessões com expiração;
- proteção contra SQL Injection;
- proteção contra XSS;
- proteção contra CSRF;
- controle de permissões no backend;
- backups criptografados;
- controle de acesso ao servidor;
- logs de segurança.

---

# 33. Autenticação

Inicialmente:

```text
usuário
senha
```

Possível evolução:

```text
usuário
senha
segundo fator
```

Profissionais poderão possuir contas pessoais e intransferíveis.

Não deve existir usuário genérico do tipo:

```text
recepcao
senha123
```

utilizado simultaneamente por várias pessoas.

---

# 34. Bloqueio de sessão

Por ser uma clínica com computadores compartilhados, deverá existir:

- logout automático após inatividade;
- botão de bloqueio rápido;
- reautenticação;
- identificação clara do usuário logado.

---

# 35. Banco de dados

Recomendação inicial:

- PostgreSQL.

Alternativas:

- MySQL/MariaDB.

PostgreSQL tende a ser adequado pela robustez, integridade relacional e possibilidade de crescimento.

---

# 36. Estrutura conceitual inicial do banco

Principais entidades:

```text
usuarios
perfis
permissoes
usuarios_perfis
perfis_permissoes

pacientes
enderecos
convenios
pacientes_convenios

profissionais
especialidades
profissionais_especialidades

agendas
agendamentos

atendimentos
filas
fila_eventos

prontuarios
evolucoes
diagnosticos
prescricoes

documentos
assinaturas

pagamentos
autorizacoes
comandas

logs_auditoria
```

---

# 37. Exemplo de relacionamento

```text
PACIENTE
   │
   ├── AGENDAMENTOS
   │
   ├── ATENDIMENTOS
   │       │
   │       ├── FILA
   │       ├── EVOLUÇÃO
   │       ├── DOCUMENTOS
   │       └── PAGAMENTO
   │
   └── HISTÓRICO
```

---

# 38. Identificadores

Evitar utilizar CPF como chave primária.

Exemplo:

```text
patient_id = UUID
```

CPF será um atributo identificador, mas o sistema possuirá ID interno próprio.

---

# 39. Exclusão de informações

Prontuários e atendimentos não deverão ser apagados diretamente.

Utilizar preferencialmente:

```text
ativo = true / false
deleted_at = timestamp
```

Quando juridicamente aplicável.

Registros clínicos deverão possuir política específica de retenção.

---

# 40. Backend

Sugestões possíveis:

## Python

- FastAPI;
- Django.

### FastAPI

Vantagens:

- API rápida;
- simples;
- documentação automática;
- boa integração com aplicações modernas.

### Django

Vantagens:

- autenticação;
- ORM;
- painel administrativo;
- estrutura madura;
- desenvolvimento rápido de sistemas administrativos.

Para um primeiro produto interno, **Django pode reduzir significativamente o tempo de desenvolvimento**.

---

# 41. Frontend

O usuário solicitou uma solução baseada em HTML.

Possibilidades:

### Opção simples

- HTML;
- CSS;
- JavaScript;
- Bootstrap;
- templates do backend.

### Opção intermediária

- HTML;
- HTMX;
- Bootstrap;
- backend Django/FastAPI.

### Opção avançada

- React/Vue;
- API separada.

Para o contexto atual, uma arquitetura com:

```text
Django + PostgreSQL + HTML + HTMX + Bootstrap
```

pode ser suficiente e manter baixa complexidade.

---

# 42. Arquitetura inicial sugerida

```text
NAVEGADORES / PAINÉIS
        │
        ├── HTTP/HTTPS
        └── WebSocket / SSE
        │
        ▼
SISTEMA WEB
Django
        │
        ├── autenticação
        ├── filas
        ├── agenda
        ├── pacientes
        ├── prontuário
        ├── documentos
        ├── chamadas em tempo real
        └── relatórios
        │
        ├──────────────► Redis / camada de eventos
        │
        ▼
PostgreSQL
```

---

# 43. Hospedagem — opção local

O servidor poderá ficar dentro da clínica.

Exemplo:

```text
Servidor local
    │
    ├── Recepção 1
    ├── Recepção 2
    ├── Recepção 3
    ├── Consultório 1
    ├── Consultório 2
    └── Consultório N
```

### Vantagens

- funcionamento sem internet externa;
- baixa latência;
- custo mensal reduzido.

### Desvantagens

- necessidade de manutenção local;
- responsabilidade por backup;
- risco físico;
- necessidade de nobreak;
- necessidade de redundância.

---

# 44. Hospedagem — opção cloud

Exemplos possíveis:

- Google Cloud;
- AWS;
- Azure;
- VPS nacional.

### Vantagens

- acesso remoto;
- backups mais simples;
- maior disponibilidade;
- expansão facilitada.

### Desvantagens

- custo mensal;
- dependência da internet;
- necessidade de configuração segura.

---

# 45. Arquitetura híbrida

Uma evolução possível:

```text
Clínica
   │
   ▼
Aplicação web
   │
   ▼
Servidor cloud
   │
   ├── banco
   ├── backups
   └── monitoramento
```

Com mecanismos locais de contingência para indisponibilidade da internet, caso sejam necessários.

---

# 46. Backup

Obrigatório.

Sugestão inicial:

- backup diário;
- backup incremental;
- retenção semanal;
- retenção mensal;
- cópia fora do servidor principal;
- teste periódico de restauração.

Backup que nunca foi testado não deve ser considerado confiável.

---

# 47. Impressão

Mesmo com digitalização, o sistema deverá permitir impressão de:

- receitas;
- atestados;
- relatórios;
- comprovantes;
- comandas;
- guias;
- senhas.

A redução do papel deverá ser gradual.

---

# 48. Migração das fichas físicas

Não é recomendável digitalizar todo o acervo antes da implantação.

Estratégia sugerida:

## Migração por demanda

Quando o paciente retornar:

1. localizar ficha física;
2. cadastrar o paciente no sistema;
3. registrar resumo relevante;
4. digitalizar documentos essenciais, se necessário;
5. passar a utilizar o prontuário eletrônico dali em diante.

Isso reduz drasticamente o custo inicial do projeto.

---

# 49. Scanner de documentos

Módulo futuro poderá permitir anexar:

- exames;
- laudos;
- documentos antigos;
- solicitações;
- termos;
- documentos externos.

Formatos:

- PDF;
- JPG;
- PNG.

---

# 50. Pesquisa global

A pesquisa deverá ser extremamente rápida.

Exemplo:

```text
Buscar paciente
> maria silva
```

Resultado:

```text
Maria da Silva
42 anos
CPF ***.***.***-**
Último atendimento: 15/08/2026
```

---

# 51. Interface

A interface deverá considerar que os usuários atuais podem possuir pouca familiaridade com sistemas complexos.

Regras:

- botões grandes;
- textos claros;
- poucas opções por tela;
- atalhos;
- cores consistentes;
- mensagens objetivas;
- confirmação apenas quando necessária.

---

# 52. Tela inicial por perfil

## Recepção

```text
[ NOVO PACIENTE ]

[ LOCALIZAR PACIENTE ]

[ CHECK-IN ]

[ FILAS ]

[ AGENDA ]
```

## Médico

```text
Minha fila

3 aguardando

[ CHAMAR PRÓXIMO ]
```

---

# 53. Notificações

Futuramente:

- confirmação de consulta;
- lembrete de consulta;
- cancelamento;
- mudança de horário;
- retorno.

Canais:

- WhatsApp;
- SMS;
- e-mail.

---

# 54. Integrações futuras

Possíveis integrações:

- WhatsApp Business API;
- serviços de SMS;
- gateways de pagamento;
- operadoras;
- assinatura digital;
- laboratórios;
- sistemas de imagem;
- plataformas de telemedicina;
- emissão fiscal;
- BI;
- APIs externas.

---

# 55. API

Mesmo que o primeiro sistema utilize HTML server-side, recomenda-se organizar o backend de forma que os principais domínios possam futuramente possuir API.

Exemplo:

```text
GET /pacientes
POST /pacientes
GET /filas
POST /atendimentos
GET /profissionais
```

---

# 56. Requisitos não funcionais

## Performance

Operações comuns devem responder rapidamente.

Meta inicial:

```text
< 2 segundos
```

em condições normais.

## Disponibilidade

O sistema deverá ser planejado para funcionar durante todo o período de atendimento da clínica.

## Escalabilidade

Deve suportar expansão para:

- mais computadores;
- mais profissionais;
- mais especialidades;
- mais unidades.

---

# 57. Observabilidade

O sistema deverá possuir:

- log de erros;
- monitoramento;
- registro de falhas;
- alertas;
- acompanhamento de desempenho.

---

# 58. Continuidade operacional

Deverá existir plano para indisponibilidade.

Exemplo:

```text
Sistema indisponível
        ↓
formulário de contingência
        ↓
atendimento continua
        ↓
dados são registrados posteriormente
```

---

# 59. MVP — primeira versão

O MVP não deverá tentar resolver todos os processos da clínica.

## MVP 1

### Cadastro

- usuários;
- profissionais;
- especialidades;
- pacientes.

### Agenda

- agenda médica;
- agendamento;
- check-in.

### Filas

- criação automática;
- fila por profissional;
- estados da fila;
- chamada do paciente.

### Prontuário

- atendimento;
- evolução;
- histórico.

### Documentos

- relatório médico;
- atestado;
- declaração;
- impressão.

### Segurança

- login;
- perfis;
- permissões;
- logs.

---

# 60. MVP 2

Adicionar:

- financeiro;
- convênios;
- comandas;
- autorizações;
- relatórios gerenciais;
- dashboard;
- anexos;
- assinatura eletrônica mais robusta.

---

# 61. MVP 3

Adicionar:

- WhatsApp;
- confirmação automática;
- painel de chamada;
- assinatura digital;
- integrações;
- BI;
- múltiplas unidades;
- gestão financeira ampliada.

---

# 62. Ordem recomendada de desenvolvimento

```text
1. autenticação
2. usuários e permissões
3. profissionais
4. especialidades
5. pacientes
6. agenda
7. check-in
8. filas
9. atendimento
10. prontuário
11. documentos
12. auditoria
13. financeiro
14. relatórios
15. integrações
```

---

# 63. Modelo inicial de módulos

```text
sgca/
│
├── accounts/
├── patients/
├── professionals/
├── specialties/
├── scheduling/
├── queues/
├── encounters/
├── medical_records/
├── documents/
├── billing/
├── reports/
├── audit/
└── core/
```

---

# 64. Regras críticas de negócio

## Regra 1

Nenhum funcionário deverá acessar informações clínicas além do necessário para sua função.

## Regra 2

Todo paciente deverá possuir cadastro permanente.

## Regra 3

O paciente não deverá precisar de uma nova ficha apenas por estar há mais de um ano sem atendimento.

## Regra 4

O histórico clínico deverá permanecer vinculado ao mesmo paciente.

## Regra 5

Todo atendimento deverá gerar registro próprio.

## Regra 6

Toda alteração relevante deverá possuir autor e data/hora.

## Regra 7

Documento assinado não deverá ser silenciosamente alterado.

## Regra 8

A posição na fila não poderá ser modificada sem registro.

## Regra 9

O médico deverá visualizar automaticamente os pacientes de sua agenda/fila.

## Regra 10

Acesso excepcional a outro prontuário deverá ser justificável e auditável.

---

# 65. Dados importantes para dimensionamento antes do desenvolvimento

Antes da implantação, deverão ser levantados:

- número médio de pacientes/dia;
- pico de pacientes/hora;
- quantidade de profissionais;
- quantidade de especialidades;
- quantidade de consultórios;
- quantidade de recepcionistas;
- quantidade de usuários simultâneos;
- quantidade de computadores;
- qualidade da rede;
- qualidade da internet;
- existência de Wi-Fi interno;
- existência de servidor;
- existência de nobreak;
- volume de prontuários físicos;
- tipos de convênios;
- fluxo de autorização;
- modelos de documentos;
- regras de retorno;
- regras de prioridade.

---

# 66. Levantamento de processo

Antes do desenvolvimento final, recomenda-se acompanhar presencialmente o fluxo de diferentes pacientes.

Cenários:

- consulta particular;
- consulta por convênio;
- paciente novo;
- paciente antigo;
- paciente com ficha localizada;
- paciente sem ficha localizada;
- duas especialidades no mesmo dia;
- encaixe;
- retorno;
- autorização recusada;
- falta;
- cancelamento.

O software deve representar o processo real e não uma versão imaginada dele.

---

# 67. Indicadores de sucesso

Após implantação, comparar:

### Antes x depois

- tempo de cadastro;
- tempo de procura de ficha;
- tempo entre chegada e médico;
- quantidade de fichas duplicadas;
- número de erros de fila;
- quantidade de papel utilizado;
- tempo gasto pela recepção;
- reclamações relacionadas à espera;
- capacidade de geração de relatórios.

---

# 68. Meta conceitual

O cenário atual:

```text
paciente
→ papel
→ arquivo
→ recepção
→ outra recepção
→ fila
→ ficha física
→ profissional
```

Cenário pretendido:

```text
paciente
→ identificação
→ sistema
→ fila digital
→ profissional
→ prontuário eletrônico
```

---

# 69. Resultado esperado

O sistema deverá transformar o prontuário físico de um objeto que precisa circular pela clínica em uma informação digital centralizada, disponível apenas para quem possui autorização.

A mudança elimina a necessidade de:

- procurar fichas em arquivos;
- mover pastas entre setores;
- criar fichas repetidas;
- depender da memória dos funcionários;
- reconstruir histórico de atendimento manualmente.

Ao mesmo tempo, possibilita:

- filas mais organizadas;
- atendimento na ordem correta;
- rastreabilidade;
- indicadores;
- histórico clínico;
- segurança;
- crescimento da operação.

---

# 70. Definição inicial do produto

**Nome do produto:** Sistema de Gestão Clínica Ambulatorial

**Tipo:** aplicação web de uso interno.

**Usuários principais:**

- recepção;
- financeiro;
- médicos;
- profissionais assistenciais;
- gestão;
- administradores.

**Stack inicial sugerida:**

```text
Backend: Django / Python
Frontend: HTML + HTMX + Bootstrap
Tempo real: Django Channels + WebSocket (ou SSE)
Mensageria/eventos: Redis, quando necessário
Banco: PostgreSQL
Servidor: Linux
Proxy: Nginx
Containers: Docker
```

**Primeiro objetivo:** digitalizar cadastro, agenda, fluxo, filas e prontuário sem alterar de forma abrupta a rotina da clínica.

---

# 71. Próximos documentos recomendados

A partir deste escopo deverão ser produzidos:

1. levantamento AS-IS do fluxo atual;
2. desenho TO-BE do fluxo futuro;
3. matriz de usuários e permissões;
4. diagrama de entidades e relacionamentos;
5. regras de negócio;
6. protótipos de tela;
7. backlog do MVP;
8. arquitetura técnica;
9. plano de implantação;
10. plano de backup e segurança;
11. política de auditoria;
12. avaliação de requisitos LGPD;
13. plano de migração gradual do papel para o digital.

---

# 72. Visão futura

Após estabilização do produto, a plataforma poderá evoluir para um sistema completo de gestão ambulatorial, incluindo:

- prontuário eletrônico;
- agendamento online;
- portal do paciente;
- resultados de exames;
- telemedicina;
- pagamentos;
- BI;
- relacionamento com pacientes;
- gestão de convênios;
- controle de faturamento;
- integração com serviços externos.

Entretanto, a primeira versão deverá priorizar exclusivamente os problemas que hoje geram maior tempo perdido e maior retrabalho:

> **localização do paciente, cadastro, fila, circulação de ficha, atendimento e registro clínico.**

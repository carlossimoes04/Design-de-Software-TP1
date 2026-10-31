# Componentes

## 1. Escolha da Abordagem e Prevenção da Entity Trap 
Para a identificação inicial dos componentes lógicos do sistema *Lisboa Pedala*, adotou-se a **abordagem Actor/Action**. Esta escolha justifica-se por o sistema possuir múltiplos atores bem diferenciados (Assinantes, Ocasionais, Técnicos, Equipa de Carrinha, Gestor Municipal e o próprio Sistema), cada um com responsabilidades e fluxos de utilização próprios. 

**Mitigação da *Entity Trap*:** 
Para evitar o antipadrão da *Entity Trap* (Aula 2 - Guia de Estudo: 9.1): 
- Evitaram-se nomes focados unicamente em entidades de base de dados ou com sufixos ambíguos/genéricos como `Manager`, `Controller`, `Handler` ou `Engine` (ex.: `ViagemManager` ou `BicicletaController`); 
- Cada componente foi nomeado e delimitado com base na **função/papel de negócio** que desempenha (ex.: `GestaoViagens`, `MonitorizacaoEstacoes`, `FaturacaoEPagamentos`), garantindo que não se tornam "depósitos" de lógica díspar.

### 1.1. Abordagem Actor/Action
| Ator | Ação Principal | Componente Lógico |
|---|---|---|
| **Utilizador (Geral)** (Assinante e Ocasional) | Desbloquear bicicleta na doca | `GestaoViagens` |
| | Devolver bicicleta na doca | `GestaoViagens` |
| | Consultar mapa de estações e bicicletas livres | `MonitorizacaoEstacoes` |
| | Consultar histórico de viagens efetuadas | `ContaUtilizador` |
| | Consultar e descarregar faturas emitidas | `FaturacaoEPagamentos` |
| | Reportar avaria de uma bicicleta | `ManutencaoFrota` |
| **Assinante** (Específico) | Associar e validar passe anual / cartão Navegante | `ContaUtilizador` |
| **Utilizador Ocasional** (Específico) | Pagar viagem pontual no momento (MB WAY / Cartão) | `FaturacaoEPagamentos` |
| **Técnico de Manutenção** | Consultar ordens de trabalho e registar reparações | `ManutencaoFrota` |
| **Equipa de Carrinha** | Consultar rotas de reequilíbrio e registar recolha/entrega | `RedistribuicaoFrota` |
| **Gestor Municipal** | Configurar regras de tarifários e passes | `GestaoTarifarios` |
| | Consultar relatórios de utilização por freguesia e emissões de $CO_2$ | `RelatoriosMunicipais` |
| **Sistema** (Automático) | Processar telemetria das bicicletas elétricas (a cada 30 s) | `MonitorizacaoEstacoes` |
| | Calcular excedentes de tempo, faturar e comunicar à AT | `FaturacaoEPagamentos` |
| | Sincronizar dados das docas guardados em modo offline | `SincronizacaoDocas` |

## 2. User Stories e respetivas componentes
As *user stories* escolhidas, para além da obrigatória (US-1), foram a US-3 e US-4:
- **US-1**: "como assinante, desbloqueio e devolvo uma bicicleta e a
viagem fica registada e cobrada"
    - **Mapeamento de componentes**:
        - **`GestaoViagens`**: regista o início da viagem no momento do desbloqueio da doca e o fecho mecânico na devolução;
        - **`ContaUtilizador`**: Valida se o passe do assinante está ativo e aplica a regra de gratuitade dos primeiros 45 minutos;
        - **`FaturacaoEPagamentos`**: Calcula o tempo total, cobra o valor dos minutos excedentes (caso existam) e emite a respetiva fatura.
- **US-3**: "como doca sem rede, reenvio os eventos guardados quando a rede volta,
sem duplicar viagens" (valida a Disponibilidade - ver 01-caracteristicas.md)
    - **Mapeamento de componentes**:
        - **`SincronizacaoDocas`**: recebe o lote de viagens guardado temporariamente na memória local da doca assim que a conetividade móvel é restabelecida;
        - **`GestaoViagens`**: processa esses registos diferidos e garante que nenhuma viagem é contabilizada ou cobrada duas vezes (garantia de idempotência).
- **US-4**: "como gestor municipal, obtenho o relatório de utilização por freguesia" (valida a Privacidade - ver 01-caracteristicas.md)
    - **Mapeamento de componentes**:
        - **`RelatoriosMunicipais`**: consolida os volumes de utilização por área geográfica e calcula a estimativa de emissões de CO₂ evitadas;
        - **`GestaoViagens`**: fornece o histórico anonimizado das rotas (apenas pontos de início e fim), garantindo que os relatórios municipais não expõem dados pessoais nem maneiras de identificar utilizadores.

## 3. Análise de Coesão (Declaração de Responsabilidade e Teste das Conjunções)
Para a análise de coesão, escolheu-se o componente mais central e carregado do sistema: **`GestaoViagens`**.

### 3.1. Responsabilidades do componente 
O componente `GestaoViagens` é responsável por validar a autorização na doca **e** registar o início da viagem, **além disso** acompanha a duração do percurso, **bem como** processa a devolução mecânica na estação de destino, **e também** calcula o valor do excedente a cobrar e envia o recibo por e-mail ao utilizador.

### 3.2. Aplicação do Teste das Conjunções
A declaração inicial **falha no teste das conjunções** devido à presença explícita dos carateres de ligação *"e"*, *"além disso"*, *"bem como"* e *"e também"*, acompanhados por excesso de vírgulas. Este texto revela a acumulação de 5 responsabilidades de domínios distintos num único componente: 
1. Validação de conta/passe; 
2. Controlo mecânico do ciclo da viagem (desbloqueio e encaixe); 
3. Acompanhamento de tempo; 
4. Cálculo de custos e cobrança; 
5. Notificação e faturação.

### 3.3. Redistribuição de responsabilidades
Para garantir **Coesão Funcional**, as responsabilidades que não pertencem ao ciclo mecânico da viagem foram retiradas e atribuídas aos respetivos componentes:
- **Validação do passe/conta:** atribuída ao componente `ContaUtilizador`; 
- **Gestão do ciclo mecânico e tempo da viagem:** mantidas como a única responsabilidade do componente `GestaoViagens`; 
- **Cálculo de custos e cobrança:** movidos para `FaturacaoEPagamentos` (em articulação com `GestaoTarifarios`); 
- **Notificação e emissão de fatura/recibo:** movidos para `FaturacaoEPagamentos`.

### 3.4. Reestruturação
O componente `GestaoViagens` tem como única responsabilidade gerir o ciclo de vida da viagem, registando o momento do desbloqueio mecânico na doca de partida, acompanhando o tempo do percurso ativo e processando o fecho de encaixe na devolução da bicicleta.

## 4. Acoplamento aferente, acoplamento eferente e instabilidade por componente

### 4.1. Acoplamento aferente e eferente
- **GestaoViagens**
  - **É chamado por** ($C_a = 2$):
    - `SincronizacaoDocas`: para registar viagens diferidas recuperadas offline;
    - `RelatoriosMunicipais`: para fornecer pontos de início/fim em anónimo.
  - **Chama** ($C_e = 3$):
    - `ContaUtilizador`: para validar conta/passe no desbloqueio;
    - `MonitorizacaoEstacoes`: para atualizar o estado ocupado/livre da doca;
    - `FaturacaoEPagamentos`: para comunicar a conclusão/duração da viagem para cálculo e cobrança.

- **ContaUtilizador**
  - **É chamado por** ($C_a = 2$):
    - `GestaoViagens`: no desbloqueio;
    - `FaturacaoEPagamentos`: para validar elegibilidade e benefícios de passe.
  - **Chama** ($C_e = 0$): nenhum

- **FaturacaoEPagamentos**
  - **É chamado por** ($C_a = 1$):
    - `GestaoViagens`: ao fechar viagem;
  - **Chama** ($C_e = 2$):
    - `GestaoTarifarios`: para obter a tabela de preços e blocos;
    - `ContaUtilizador`: para confirmar dados do perfil/plano.

- **MonitorizacaoEstacoes**
  - **É chamado por** ($C_a = 2$):
    - `GestaoViagens`: na alteração de estado das docas;
    - `RedistribuicaoFrota`: para ler a lotação em tempo real.
  - **Chama** ($C_e = 1$):
    - `ManutencaoFrota`: ao detetar/receber alerta de avaria numa doca ou bicicleta via telemetria.

- **GestaoTarifarios**
  - **É chamado por** ($C_a = 1$):
    - `FaturacaoEPagamentos`: para consultar as regras de preços e minutos grátis.
  - **Chama** ($C_e = 0$): contém apenas a parametrização de tarifários; não depende de nenhum outro componente.

- **ManutencaoFrota**
  - **É chamado por** ($C_a = 1$):
    - `MonitorizacaoEstacoes`: para abertura automática de ordens de trabalho.
  - **Chama** ($C_e = 0$): isolado; gere autonomamente o ciclo das ordens de trabalho.

- **RedistribuicaoFrota**
  - **É chamado por** ($C_a = 0$): nenhum componente interno depende dele (ponto de consumo das carrinhas).
  - **Chama** ($C_e = 1$):
    - `MonitorizacaoEstacoes`: para ler a ocupação atual de todas as estações.

- **RelatoriosMunicipais**
  - **É chamado por** ($C_a = 0$): nenhum componente interno depende dele (ponto de consumo do Gestor Municipal).
  - **Chama** ($C_e = 1$):
    - `GestaoViagens`: para extrair dados anónimos de viagens.

- **SincronizacaoDocas**
  - **É chamado por** ($C_a = 0$): ponto de entrada de eventos físicos das docas.
  - **Chama** ($C_e = 1$):
    - `GestaoViagens`: para submeter em lote as viagens acumuladas em modo offline.

### 4.2. Instabilidade por componente ($I = \frac{C_e}{C_a + C_e}$)
| Componente Lógico | $C_a$ (Aferente) | $C_e$ (Eferente) | Instabilidade ($I$) | Classificação Arquitetural |
|---|:---:|:---:|:---:|---|
| `GestaoTarifarios` | 1 | 0 | **0,00** | **Totalmente Estável** |
| `ManutencaoFrota` | 1 | 0 | **0,00** | **Totalmente Estável** |
| `ContaUtilizador` | 2 | 0 | **0,00** | **Totalmente Estável** |
| `MonitorizacaoEstacoes` | 2 | 1 | **0,33** | **Estável** |
| `FaturacaoEPagamentos` | 1 | 2 | **0,67** | **Moderadamente Instável** |
| `GestaoViagens` | 2 | 3 | **0,60** | **Moderadamente Instável** |
| `RedistribuicaoFrota` | 0 | 1 | **1,00** | **Totalmente Instável** |
| `RelatoriosMunicipais` | 0 | 1 | **1,00** | **Totalmente Instável** |
| `SincronizacaoDocas` | 0 | 1 | **1,00** | **Totalmente Instável** |

- **Componentes de base** (estáveis) ($I \le 0{,}33$): `GestaoTarifarios`, `ContaUtilizador` e `MonitorizacaoEstacoes` guardam a informação essencial do sistema. Como vários módulos dependem deles, qualquer mudança na forma como comunicam exige muito cuidado para não estragar o que já funciona;
- **Componentes de coordenação** (moderadamente instáveis) ($I = 0{,}60$ a $0{,}67$): `GestaoViagens` e `FaturacaoEPagamentos` gerem as ações do utilizador no dia a dia. Estão no meio da ponte: pedem dados aos componentes de base e fornecem informação aos componentes finais;
- **Componentes independentes** (fáceis de mudar) ($I = 1{,}00$): `RedistribuicaoFrota`, `RelatoriosMunicipais` e `SincronizacaoDocas` tratam de tarefas específicas. Como nenhum outro módulo depende deles para funcionar, podem ser alterados ou reescritos por completo sem qualquer risco para o resto da aplicação;

## 5. Conascência, Acoplamento Temporal, Lei de Deméter e Reestruturação 
### 5.1. Conascência entre Componentes 
Dois componentes apresentam conascência quando uma alteração num exige uma alteração no outro para manter o funcionamento correto do sistema (Meilir Page-Jones; Richards & Ford, Cap. 3).

A gravidade do acoplamento por conascência é avaliada através de três propriedades fundamentais (Page-Jones / Jim Weirich):
- **Força (Strength)**: mede a facilidade com que o programador descobre e refatora o acoplamento. As formas estáticas mais fracas são Nome e Tipo; as formas estáticas mais fortes são Significado e Algoritmo; as conascências dinâmicas (de execução, tempo ou valor) são as mais gravosas;
- **Grau (Degree)**: mede o impacto pelo número de entidades envolvidas. Graus reduzidos têm impacto contido; graus elevados multiplicam o risco de falhas em cascata;
- **Localidade (Locality)**: mede a proximidade física e arquitetural no código. Conascências fortes são perfeitamente aceitáveis se a localidade for próxima (dentro do mesmo módulo), mas tornam-se críticas quando atravessam fronteiras de pacotes. A regra de Page-Jones dita: *minimizar a conascência que cruza fronteiras e maximizar a conascência interna aos módulos*.

Identificámos e mitigámos duas conascências centrais no sistema Lisboa Pedala:
1. **Conascência de Significado (CoM - *Connascence of Meaning*):** 
    - **Componentes envolvidos:** `MonitorizacaoEstacoes` e `ManutencaoFrota`;
    - **Descrição:** ambos os componentes partilham a mesma convenção/significado para o estado operacional das bicicletas e docas (ex.: as cadeias de texto `"LIVRE"`, `"AVARIADA"`, `"EM_MANUTENCAO"`); 
    - **Avaliação das Propriedades**:
      - *Força*: **média/elevada** (forma estática). Se uma das pontas alterar a string livre, o compilador e o linter não detetam o erro de imediato;
      - *Grau*: **grau 2** (baixo), restrito à coordenação entre os dois componentes;
      - *Localidade*: *distante*, pois atravessa a fronteira entre dois pacotes de domínio distintos (`src/estacoes/` e `src/manutencao/`), aumentando o perigo de desalinhamento.
    - **Risco de Acoplamento:** se o `MonitorizacaoEstacoes` alterar o nome interno do estado de avaria para `NAO_OPERACIONAL` e o `ManutencaoFrota` não for atualizado em simultâneo, a criação automática de ordens de trabalho falha;
    - **Mitigação:** substituição de texto livre por um enumerado (`Enum`) partilhado ou contrato de API estritamente tipado. 
2. **Conascência de Algoritmo (CoA - *Connascence of Algorithm*):**
    - **Componentes envolvidos:** `SincronizacaoDocas` e `GestaoViagens`
    - **Descrição:** Para responder à **US-3** (operação offline), a doca calcula um código de identificação único para cada viagem armazenada localmente. Tanto o `SincronizacaoDocas` como o `GestaoViagens` têm de usar **exatamente o mesmo algoritmo de cálculo de hash** (ex.: `SHA-256(docaId + bicicletaId + timestampInicio)`) para detetar e ignorar registos duplicados; 
    - **Avaliação das Propriedades**:
      - *Força*: **máxima entre as conascências estáticas** Uma discrepância subtil na concatenação ou codificação quebra a deteção de duplicados sem originar exceções imediatas;
      - *Grau*: **grau 2 a 3** (baixo a moderado: software da doca, módulo de sincronização e backend de viagens);
      - *Localidade*: **próxima no backend**, (ambos residem em `src/viagens/`), mas **distante na simulação** (comunicação entre a doca e o servidor central).
    - **Risco de Acoplamento:** Se o `SincronizacaoDocas` alterar a fórmula do hash sem o `GestaoViagens` atualizar a sua validação, a deteção de duplicados falha e o utilizador pode ser cobrado duas vezes;
    - **Mitigação:** Isolamento do algoritmo numa biblioteca de utilidade única e partilhada.

### 5.2. Acoplamento Temporal 
O acoplamento temporal descreve dependências que exigem uma ordem específica no tempo ou a execução dentro da mesma transação. 
1. **Acoplamento Temporal de Ordem:** 
    - **Componentes:** `ContaUtilizador` $\rightarrow$ `GestaoViagens`
    - **Descrição:** no processo de desbloqueio, a verificação do passe e da conta em `ContaUtilizador` tem de ocorrer **obrigatoriamente antes** da libertação física da tranca em `GestaoViagens`. Inverter a ordem permitiria libertar bicicletas antes de validar se o utilizador tem permissão; 
2. **Acoplamento Temporal de Transação:** 
    - **Componentes:** `GestaoViagens` $\leftrightarrow$ `MonitorizacaoEstacoes` 
    - **Descrição:** na devolução da bicicleta, o fecho da viagem em `GestaoViagens` e a alteração do estado da doca de "OCUPADA" para "LIVRE" em `MonitorizacaoEstacoes` têm de ser executados **na mesma unidade de trabalho**. Se a transação falhar a meio, a doca pode ficar bloqueada no sistema ou a viagem continuar ativa indevidamente.

### 5.3. Aplicação da Lei de Deméter (Princípio do Menor Conhecimento)
A **Lei de Deméter (LoD)**, ou *Princípio do Menor Conhecimento* (Aula 4; Richards & Ford, Cap. 8), estabelece que um componente deve possuir conhecimento limitado sobre outros componentes, interagindo exclusivamente com os seus colaboradores/vizinhos imediatos ("falar apenas com amigos próximos e nunca com os amigos dos amigos").

No sistema Lisboa Pedala, a Lei de Deméter foi fundamental para evitar acoplamento desnecessário e dispersão de regras de negócio:

1. **Desacoplamento do Ciclo de Viagem e Faturação** (`GestaoViagens` $\rightarrow$ `FaturacaoEPagamentos`):
    - **Violação evitada**: se a LoD fosse ignorada, o componente `GestaoViagens`, ao processar a devolução mecânica, teria de conhecer as regras de negócio de `GestaoTarifarios` (os 45 min grátis do passe anual e os blocos de 15 min), inspecionar os métodos de pagamento em `ContaUtilizador`, invocar diretamente a Gateway de Pagamentos e registar a comunicação com a Autoridade Tributária. Isto tornaria `GestaoViagens` fortemente acoplado a regras fiscais e financeiras voláteis;
    - **Aplicação da LoD**: o `GestaoViagens` limita-se a produzir e enviar o resumo da viagem (`viagem_id`, `utilizador_id`, `duracao_minutos`) ao seu vizinho imediato, `FaturacaoEPagamentos`. O `GestaoViagens` **não sabe nem precisa de saber** se a viagem tem custo, como se calculam excedentes ou como é feita a cobrança. É o `FaturacaoEPagamentos` que encapsula todo o conhecimento do domínio financeiro.
2. **Desacoplamento na Autorização de Desbloqueio** (`GestaoViagens` $\rightarrow$ `ContaUtilizador`):
    - O `GestaoViagens` não inspeciona a estrutura interna do utilizador (se tem faturas pendentes, NIF, saldo ou data de renovação do passe). Comunica unicamente através do método de consulta direta `validar_permissao_desbloqueio(utilizador_id)` em `ContaUtilizador`, recebendo apenas a resposta booleana necessária para libertar a tranca.
3. **Impacto Arquitetural - Redistribuição do Acoplamento**:
    - Como destacado na Aula 4, **a Lei de Deméter redistribui o acoplamento, não o elimina**. Ao retirar o conhecimento tarifário de `GestaoViagens`, esse acoplamento transferiu-se para `FaturacaoEPagamentos` (que passa a chamar `GestaoTarifarios` e `ContaUtilizador`);
    - **Ganho de Localidade**: ganhámos em coesão e localidade: alterações fiscais ou novos planos tarifários das câmaras municipais mudam exclusivamente no módulo `faturacao`, sem afetar o ciclo crítico de desbloqueio e devolução de bicicletas.

### 5.4. Iteração de Reestruturação Documentada 
- **Componente Afetado:** `GestaoViagens` 
- **Motivo da Reestruturação:** na versão inicial do design, o componente `GestaoViagens` acumulava a responsabilidade mecânica da viagem, a validação de passes e o cálculo financeiro/emissão de recibos. Esta acumulação violava a **Coesão Funcional** (falhando no *Teste das Conjunções*) e criava um acoplamento eferente ($C_e$) excessivo com sistemas de pagamento e notificações. 
- **Ação de Refactoring Aplicada:** 
    1. Extração da validação de elegibilidade e passe para o componente `ContaUtilizador`;
    2. Extração do cálculo de tarifários excedentes, cobrança e emissão de fatura para o componente `FaturacaoEPagamentos`;
    3. **Resultado:** O `GestaoViagens` passou a ter como única responsabilidade a gestão do ciclo de vida da viagem (desbloqueio, tempo decorrido e devolução na doca), reduzindo a sua complexidade, aumentando a sua coesão interna e isolando as regras financeiras num módulo próprio.
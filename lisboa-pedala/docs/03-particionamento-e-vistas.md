# Particionamento e Vistas

## 1. Particionamento de topo: por domínio
Para organizar o código do projeto, escolhemos a **organização por domínio** (separado pelas áreas de negócio, como `viagens`, `estacoes` e `faturacao`), em vez de um **particionamento técnico** (separado por camadas técnicas como `controllers`, `services` e `repositories`).

- **O código mostra logo o que a aplicação faz:** ao olhar para as pastas principais, percebe-se imediatamente o objetivo do *Lisboa Pedala* (`viagens`, `estacoes`), em vez de se verem apenas nomes de ferramentas técnicas;
- **As alterações ficam arrumadas no mesmo sítio:** se a regra de devolução de uma bicicleta mudar, mexemos apenas na pasta `viagens/`. Não temos de andar a saltar entre várias pastas técnicas para mudar uma única funcionalidade;
- **Divisão fácil do trabalho na equipa:** cada membro do grupo pode trabalhar numa área do sistema sem estar a alterar os mesmos ficheiros ao mesmo tempo que os colegas;
- **Facilidade em separar o sistema no futuro:** como o código fica guardado em blocos bem definidos, se mais tarde for preciso isolar um módulo num servidor próprio, a divisão já está feita.

### 1.1. Estrutura de pastas no Python 3.11 
```text 
lisboa-pedala/ 
├── src/ 
│   ├── viagens/         # GestaoViagens e SincronizacaoDocas 
│   ├── utilizadores/    # ContaUtilizador 
│   ├── estacoes/        # MonitorizacaoEstacoes e RedistribuicaoFrota 
│   ├── faturacao/       # FaturacaoEPagamentos e GestaoTarifarios 
│   ├── manutencao/      # ManutencaoFrota 
│   ├── relatorios/      # RelatoriosMunicipais 
│   └── shared/          # Utilitários técnicos comuns, DB (SQLite) e DTOs 
├── tests/ 
│   └── architecture/    # Fitness Functions com import-linter 
├── docs/                # Documentação e ADRs 
└── .importlinter        # Configuração de contratos de arquitetura
```

### 1.2. *Trade-offs*
- **As mudanças técnicas globais dão mais trabalho:** se quisermos mudar a base de dados ou a tecnologia da interface em todo o sistema, vamos ter de atualizar ficheiros espalhados por várias pastas de domínio;
- **Exige cuidado com o código repetido:** é preciso disciplina para colocar o código comum (como a ligação à base de dados ou o tratamento de erros) numa pasta partilhada (`shared/`), evitando duplicar código pelas restantes pastas.

## 2. Vista de módulos (com regras *Allowed-to-Use*) 
A vista de módulos mostra como o código está organizado em pastas e ficheiros e define **quem tem autorização para importar quem**. O objetivo destas regras de permissão (*allowed-to-use*) é evitar que os módulos fiquem todos dependentes uns dos outros, impedindo a criação de ligações em ciclo e código difícil de alterar.

### 2.1. Identificação e papel dos módulos

| Módulo (Diretório/Namespace) | Componentes Lógicos Abrangidos | Responsabilidade Principal |
| :--- | :--- | :--- |
| **`viagens`** | `GestaoViagens`, `SincronizacaoDocas` | Gerir o ciclo de vida da viagem (desbloqueio, contagem de tempo e devolução) e processar eventos de docas offline. |
| **`utilizadores`** | `ContaUtilizador` | Gerir dados dos utilizadores, validação de passes anuais e cartões Navegante. |
| **`estacoes`** | `MonitorizacaoEstacoes`, `RedistribuicaoFrota` | Acompanhar a lotação e estado das docas em tempo real e calcular rotas de reequilíbrio para as carrinhas. |
| **`faturacao`** | `FaturacaoEPagamentos`, `GestaoTarifarios` | Configurar tarifários, calcular custos excedentes de viagem, cobrar pagamentos e emitir faturas. |
| **`manutencao`** | `ManutencaoFrota` | Registar relatórios de avaria, gerir o estado de reparação das bicicletas e ordens de trabalho dos técnicos. |
| **`relatorios`** | `RelatoriosMunicipais` | Consolidação analítica e anónima de dados de utilização por freguesia e estimativa de CO₂ para a Câmara. |
| **`shared`** | *Código comum* | Utilitários técnicos (conexão ao SQLite, erros e DTOs globais). Não contém regras de negócio. |

### 2.2. Tabela de permissões de importação (*Allowed-to-Use*) 
| Módulo de Código | Pode Importar / Utilizar (*Allowed-to-Use*) | Importações Proibidas (Exemplos) | 
| :--- | :--- | :--- | 
| **`viagens`** | `utilizadores`, `estacoes`, `faturacao`, `shared` | **Proibido importar** `relatorios` e `manutencao`. | 
| **`utilizadores`** | `shared` | **Proibido importar** `viagens`, `estacoes` e `faturacao`. | 
| **`faturacao`** | `utilizadores`, `shared` | **Proibido importar** `viagens` (recebe os dados da viagem por parâmetro para evitar ciclos). |
| **`estacoes`** | `manutencao`, `shared` | **Proibido importar** `faturacao`, `viagens` e `relatorios`. |
| **`manutencao`** | `shared` | Módulo autónomo; **proibido importar qualquer outro módulo de negócio**. |
| **`relatorios`** | `viagens`, `shared` | **Proibido alterar dados** ou importar `faturacao` e `manutencao` diretamente. |
| **`shared`** | *Nenhum módulo de negócio* | É o módulo utilitário base e **não pode importar nenhum módulo de domínio**. |

## 3. Vista de componentes e conectores de fluxo
Esta vista mostra como o sistema funciona **em tempo de execução** para o fluxo principal do utilizador (**US-1**). Divide-se em dois conceitos simples: 
- **Componentes:** as partes do programa que estão ativas e a correr no momento;
- **Conectores:** as ligações e protocolos que permitem a esses componentes falar uns com os outros.

### 3.1. Identificação de Componentes e Conectores 
#### Componentes (O que está a correr) 
- **Cliente de interface (CLI / API REST):** interface em linha de comandos (CLI) ou cliente HTTP REST que permite invocar as operações sem necessidade de interface gráfica;
- **Módulos do Servidor (** **GestaoViagens** **,** **ContaUtilizador** **,** **MonitorizacaoEstacoes** **,** **FaturacaoEPagamentos** **,** **GestaoTarifarios** **):** componentes lógicos a correr no processo Python;
- **Simulador de Docas Físicas:** componente de simulação em Python que emite os sinais de encaixe/desencaixe de bicicletas;
- **Simulador de Gateway de Pagamentos:** componente de simulação (*stub*) em Python que processa cobranças de MB WAY / Cartão sem dependência de serviços externos reais;
- **Base de Dados (SQLite / Em Memória):** armazenamento relacional local

#### Conectores (Como comunicam) 
- **CLI / HTTP REST:** canal de invocação de operações pelo utilizador ou cliente externo; 
- **Chamada de Método Interno (in-process):** chamadas síncronas diretas de funções/métodos Python entre componentes no mesmo processo; 
- **Driver SQLite / Python DB-API:** canal de acesso e persistência de dados

### 3.2. Passo a Passo do Fluxo (US-1)
1. **Desbloquear (Início da Viagem):**
    - O utilizador solicita o desbloqueio da bicicleta através da **CLI / API REST**;
    - O **GestaoViagens** recebe o pedido e faz uma chamada interna ao **ContaUtilizador** para validar se o passe está ativo;
    - Após a validação, o **GestaoViagens** invoca o **Simulador de Doca** para libertar a tranca física e regista a hora de início da viagem no **SQLite**.
2. **Devolver (Fim da Viagem):**
    - O **Simulador de Doca** sinaliza o encaixe mecânico da bicicleta ao **GestaoViagens**;
    - O **GestaoViagens** calcula a duração total da viagem, fecha o registo e avisa o **MonitorizacaoEstacoes** para atualizar o estado da doca para "LIVRE".
3. **Cobrar (Cálculo e Pagamento):**
    - O **GestaoViagens** passa os dados da viagem concluída ao **FaturacaoEPagamentos**;
    - O **FaturacaoEPagamentos** consulta o **GestaoTarifarios** para verificar o período gratuito (ex.: 45 min);
    - Havendo excedente, o **FaturacaoEPagamentos** invoca o **Simulador de Gateway de Pagamentos** para processar a cobrança e grava a fatura na base de dados **SQLite**.

## 4. Vista de alocação (infraestrutura e CODEOWNERS) 
Esta vista descreve onde cada parte do sistema corre fisicamente na infraestrutura e como a responsabilidade do código está dividida entre os **dois elementos do grupo**.

###  4.1. Mapeamento físico (onde corre cada parte) 
- **Ambiente de Execução Python 3.11:** o backend corre como um processo Python 3.11 num ambiente local ou contentorizado;
- **Interface do Utilizador:** cliente CLI ou pontos de extremidade API REST HTTP (sem necessidade de GUI);
- **Persistência de Dados:** base de Dados **SQLite** em ficheiro local (`lisboa_pedala.db`) ou em memória para testes, dispensando servidores de base de dados pesados (como MySQL/PostgreSQL);
- **Simulação de Periféricos e Serviços Externos:** as Docas Físicas (IoT) e a Gateway de Pagamentos são implementadas como **Módulos de Simulação em Python**, cumprindo o âmbito simplificado do protótipo

### 4.2. Atribuição de Responsabilidades na Equipa (`CODEOWNERS`)
Dividimos os 9 componentes lógicos de forma equilibrada entre os **dois elementos do grupo**: 
| Diretório / Módulo | Componentes Lógicos | Elemento Responsável | 
| :--- | :--- | :--- | 
| **`src/viagens/`** | `GestaoViagens` e `SincronizacaoDocas` | **Aluno 1** | 
| **`src/utilizadores/`** | `ContaUtilizador` | **Aluno 1** | 
| **`src/relatorios/`** | `RelatoriosMunicipais` | **Aluno 1** | 
| **`src/faturacao/`** | `FaturacaoEPagamentos` e `GestaoTarifarios` | **Aluno 2** | 
| **`src/estacoes/`** | `MonitorizacaoEstacoes` e `RedistribuicaoFrota` | **Aluno 2** | 
| **`src/manutencao/`** | `ManutencaoFrota` | **Aluno 2** | 
| **`src/shared/`** | Código comum, utilitários e ligação à BD | **Aluno 1 e Aluno 2** *(Trabalho conjunto)* |
| **`tests/architecture/`** | Fitness Functions (`import-linter`) | **Aluno 1 e Aluno 2** *(Trabalho conjunto)*

### Razão desta Divisão
- **Equilíbrio de trabalho:** cada elemento fica responsável por 4 a 5 componentes com complexidade semelhante; 
- **Trabalho em equipa sem conflitos no Git:** como os ficheiros estão em pastas de domínio separadas, cada um pode trabalhar no seu módulo sem alterar os ficheiros do colega ao mesmo tempo.
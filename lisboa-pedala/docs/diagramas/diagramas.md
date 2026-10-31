# Diagramas C4 - Níveis 1 a 3

Este documento contem a arquitetura do sistema **Lisboa Pedala** através do modelo C4 (Níveis 1 a 3). O objetivo é mostrar a estrutura da aplicação com diferentes graus de detalhe, desde a interação com os utilizadores até à organização interna do código.

A documentação divide-se em três níveis progressivos de abstração: 
- **Nível 1: Diagrama de Contexto (*System Context*)** - apresenta o sistema como um todo no centro da operação, identificando os 5 perfis de utilizadores (assinantes, ocasionais, técnicos, equipa de carrinha e gestores) e a ligação aos serviços externos simulados (docas IoT e pagamentos);
- **Nível 2: Diagrama de Contentores (*Containers*)** - mostra onde o sistema corre na prática, detalhando o cliente de interface (CLI / API REST), o processo central em Python 3.11 e a base de dados local em SQLite; 
- **Nível 3: Diagrama de Componentes (*Components*)** - faz um *zoom* sobre o servidor para ilustrar a interação entre os 9 componentes lógicos na pasta `src/` durante o fluxo principal da **US-1** (`Desbloquear → Devolver → Cobrar`).

## Diagrama C4 - Nível 1
```mermaid
graph TD

%% Atores
uAssinante["<b>Assinante (Passe Anual)</b><br />[Pessoa]<br />Desbloqueia bicicletas com cartão Navegante ou App"]
uOcasional["<b>Utilizador Ocasional</b><br />[Pessoa]<br />Paga viagens pontuais com MB WAY / Cartão"]
uTecnico["<b>Técnico de Manutenção</b><br />[Pessoa]<br />Gere ordens de reparação de bicicletas"]
uCarrinha["<b>Equipa de Carrinha</b><br />[Pessoa]<br />Reequilibra a lotação entre estações"]
uGestor["<b>Gestor Municipal</b><br />[Pessoa]<br />Consulta relatórios e define tarifários"]

%% Sistema Central
sysLisboa["<b>Sistema Lisboa Pedala</b><br />[Sistema de Software]<br />Gere o desbloqueio, devolução, faturação, manutenção e estatísticas de bicicletas partilhadas."]

%% Sistemas Externos
extDoca["<b>Doca Física (Simulada)</b><br />[Sistema Externo]<br />Controla o encaixe/desencaixe físico da bicicleta"]
extPagamentos["<b>Gateway de Pagamentos (Simulado)</b><br />[Sistema Externo]<br />Processa cobranças de MB WAY e Cartão"]
extAT["<b>Autoridade Tributária (Simulada)</b><br />[Sistema Externo]<br />Recebe comunicação de faturas emitidas"]

%% Relações
uAssinante -->|"Desbloqueia e devolve bicicletas"| sysLisboa
uOcasional -->|"Paga e utiliza bicicletas"| sysLisboa
uTecnico -->|"Consulta e fecha avarias"| sysLisboa
uCarrinha -->|"Consulta rotas de reequilíbrio"| sysLisboa
uGestor -->|"Analisa relatórios de CO₂ e freguesias"| sysLisboa

sysLisboa -->|"Envia comandos de abertura e recebe encaixe"| extDoca
sysLisboa -->|"Pede cobrança de tarifas excedentes"| extPagamentos
sysLisboa -->|"Comunica dados de faturação"| extAT

%% Legenda
subgraph Legenda["Legenda"]
    direction LR
    legPessoa["[Pessoa] Ator Humano"]
    legSys["[Sistema de Software] Sistema Principal"]
    legExt["[Sistema Externo] Periférico / Serviço Simulado"]
end
```
---
## Diagrama C4 - Nível 2
```mermaid
graph TD

%% Atores
uUser["<b>Utilizadores e Técnicos</b><br />[Pessoas]<br />Assinantes, Ocasionais, Técnicos, Carrinhas e Gestores"]

subgraph LisboaPedala["Sistema Lisboa Pedala (Fronteira do Sistema)"]

    %% Contentores Internos
    cCLI["<b>Cliente CLI / API REST</b><br />[Contentor: Python 3.11 / HTTP]<br />Interface em linha de comandos ou API REST para interagir com o sistema (sem GUI)"]

    cBackend["<b>Backend Monólito Modular</b><br />[Contentor: Processo Python 3.11]<br />Processo central que executa a lógica de negócio organizada pelos pacotes de domínio em src/"]

    cDB[("<b>Base de Dados Relacional</b><br />[Contentor: SQLite / Em Memória]<br />Armazena dados de utilizadores, viagens, estações, faturas e avarias num ficheiro local (.db)")]

end

%% Contentores Externos
cSimDoca["<b>Simulador de Doca </b><br />[Contentor: Módulo Python]<br />Simula o sinal mecânico de abertura de tranca e encaixe de devolução"]

cSimPag["<b>Simulador Gateway Pagamentos</b><br />[Contentor: Módulo Python]<br />Simula a resposta de autorização de cobrança MB WAY / Cartão"]

%% Relações
uUser -->|"Executa comandos ou pedidos HTTP"| cCLI
cCLI -->|"Invocação de métodos / REST"| cBackend
cBackend -->|"Lê e escreve dados [Python DB-API]"| cDB
cBackend -->|"Envia ordens de abertura e recebe eventos de devolução"| cSimDoca
cBackend -->|"Solicita cobrança de minutos excedentes"| cSimPag

%% Legenda
subgraph Legenda["Legenda"]
    direction LR
    legCont["[Contentor] Aplicação ou Processo Executável"]
    legDB["[Base de Dados] Armazenamento Relacional Local"]
    legExt["[Contentor Simulado] Periférico / Serviço Externo"]
end
```
---
## Diagrama C4 - Nível 3

```mermaid
graph TD

%% Containers Externos
cCLI["<b>Cliente CLI / API REST</b><br />[Container: Python 3.11 / HTTP]"]
cSimDoca["<b>Simulador de Doca</b><br />[Container: Módulo Python]"]
cSimPag["<b>Simulador Gateway Pagamentos</b><br />[Container: Módulo Python]"]
cDB[("<b>Base de Dados Relacional</b><br />[Container: SQLite / Em Memória]")]

%% Decomposição do Container Backend Monólito Modular
subgraph cBackend["Container: Backend Monólito Modular (Processo Python 3.11)"]

    %% Módulos de Domínio
    cmpViagens["<b>GestaoViagens</b><br />[Componente: src/viagens/]<br />Gere o ciclo mecânico e temporal da viagem"]

    cmpSincronia["<b>SincronizacaoDocas</b><br />[Componente: src/viagens/]<br />Processa em lote eventos de docas offline (US-3)"]

    cmpConta["<b>ContaUtilizador</b><br />[Componente: src/utilizadores/]<br />Valida passes anuais e cartões Navegante"]

    cmpEstacoes["<b>MonitorizacaoEstacoes</b><br />[Componente: src/estacoes/]<br />Acompanha o estado e lotação de docas"]

    cmpRedistribuicao["<b>RedistribuicaoFrota</b><br />[Componente: src/estacoes/]<br />Calcula rotas de reequilíbrio para carrinhas"]

    cmpFaturacao["<b>FaturacaoEPagamentos</b><br />[Componente: src/faturacao/]<br />Calcula excedentes, cobra e emite faturas"]

    cmpTarifarios["<b>GestaoTarifarios</b><br />[Componente: src/faturacao/]<br />Guarda regras de preços e minutos grátis"]

    cmpManutencao["<b>ManutencaoFrota</b><br />[Componente: src/manutencao/]<br />Gere ordens de reparação de bicicletas"]

    cmpRelatorios["<b>RelatoriosMunicipais</b><br />[Componente: src/relatorios/]<br />Consolida dados anónimos para a Câmara"]

    cmpShared["<b>Shared / Infraestrutura</b><br />[Componente: src/shared/]<br />Conexão SQLite, erros e DTOs utilitários"]

    cmpBackendComun["Todos os componentes de domínio"]

end

%% Relações do Cliente e Simuladores Externos com os Componentes
cCLI -->|"Invoca comandos / pedidos"| cmpViagens
cCLI -->|"Consulta conta e passes"| cmpConta
cCLI -->|"Consulta relatórios"| cmpRelatorios
cCLI -->|"Gere ordens de trabalho"| cmpManutencao

cmpViagens -->|"Envia comandos e recebe fecho"| cSimDoca
cmpSincronia -->|"Lê eventos diferidos"| cSimDoca
cmpFaturacao -->|"Pede autorização de cobrança"| cSimPag

%% Dependências Estáticas Internas
cmpViagens -->|"Valida passe ativo"| cmpConta
cmpViagens -->|"Atualiza estado da doca"| cmpEstacoes
cmpViagens -->|"Notifica viagem concluída"| cmpFaturacao

cmpSincronia -->|"Submete viagens recuperadas"| cmpViagens

cmpFaturacao -->|"Consulta tabela de preços"| cmpTarifarios
cmpFaturacao -->|"Consulta dados do utilizador"| cmpConta

cmpEstacoes -->|"Reporta avaria física"| cmpManutencao

cmpRedistribuicao -->|"Lê ocupação em tempo real"| cmpEstacoes

cmpRelatorios -->|"Lê histórico anónimo de viagens"| cmpViagens

%% Acesso à Base de Dados via Shared
cmpBackendComun -.->|"Acedem via DB-API"| cmpShared
cmpShared -.->|"Lê e escreve dados"| cDB

%% Legenda
subgraph Legenda["Legenda"]
    direction LR
    legCont["[Container Externo] Executável / Armazenamento"]
    legCmp["[Componente Lógico] Pacote Python em src/"]
    legDep["──► Dependência Estática / Invocação"]
    legDbAcc["- -► Conexão de Persistência"]
end
```
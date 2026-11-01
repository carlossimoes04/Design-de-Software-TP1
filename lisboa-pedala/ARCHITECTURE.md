# Especificação da Arquitetura

Este documento constitui a especificação de arquitetura do sistema *Lisboa Pedala*. Todo o código gerado deve cumprir com estas regras, convenções, acoplamentos e restrições aqui definidos. Qualquer desvio resulta em falhas nas *fitness functions* e rejeição do código.  
Todo o código gerado deve respeitar integralmente as regras aqui descritas. Nenhuma violação das regras *allowed-to-use* ou das restrições arquiteturais é permitida. Cada geração de componente deve consultar os ADRs indicados.

## 1. Identificação e Papel dos Componentes

O sistema está dividido em domínios em **9 componentes lógicos** distribuídos nos respetivos pacotes Python em `src/`:

|Componente Lógico|Pacote / Namespace|Responsabilidade|
|:---|:---|:---|
|`GestaoViagens`|`src.viagens.gestao_viagens`|Orquestra o ciclo da vida completo de desbloqueio, acompanhamento e fecho de viagens de bicicletas.|
|`SincronizacaoDocas`|`src.viagens.sincronizacao_docas`|Processa e desduplica registos diferidos de viagens enviados em lote pelas docas offline.|
|`ContaUtilizador`|`src.utilizadores.conta_utilizador`|Valida passes, gere estados de utilizadores e autentica pedidos de utilização.|
|`MonitorizacaoEstacoes`|`src.estacoes.monitorizacao_estacoes`|Gere a ocupação, o estado mecânico das docas e o inventário em tempo real por estação.|
|`RedistribuicaoFrota`|`src.estacoes.redistribuicao_frota`|Calcula e sugere rotas otimizadas às carrinhas municipais para haver um equilíbrio na frota.|
|`FaturacaoEPagamentos`|`src.faturacao.faturacao_pagamentos`|Simula a cobrança financeira e emite faturas em conformidade com a Autoridade Tributária (AT).|
|`GestaoTarifarios`|`src.faturacao.gestao_tarifarios`|Aplica as regras de cálculo de custo base e excedentes por patamar de tempo e tipo de utilizador.|
|`ManutencaoFrota`|`src.manutencao.manutencao_frota`|Gere o ciclo de vida das ordens de trabalho e avarias reportadas para reparação de bicicletas.|
|`RelatoriosMunicipais`|`src.relatorios.relatorios_municipais`|Compila estatísticas anónimas de utilização por freguesia e estima o $CO_2$ evitado.|

*Nota*: O pacote utilitário partilhado reside em `src.shared` e contém a conectividade SQLite, modelos DTOs e utilitários de encriptação / *hashing*.

---



## 2. Regras *Allowed-to-Use* (Contratos de Importação Imperativos)

Em conformidade com o **ADR-007**, as dependências entre pacotes formam um Grafo Acíclico Dirigido (DAG). As regras seguintes são **verificáveis por *fitness functions* (`import-linter`) e constituem restrições duras**:

```
                 [src.relatorios]
                        │
                        ▼
                 [src.viagens] ──────────────────────────┐
                  │          │                           │
                  ▼          ▼                           ▼
           [src.estacoes]  [src.faturacao] ────► [src.utilizadores]
                  │
                  ▼
           [src.manutencao]

═══════════════════════════════════════════════════════════════════
[src.shared] (camada utilitária base — importada por todos os módulos)
```

### Regras Estritas de Importação:
1. **`src.viagens`:**
   - **Pode importar:** `src.utilizadores`, `src.estacoes`, `src.faturacao`, `src.shared`.
   - **Proibido importar:** `src.relatorios`, `src.manutencao`.
2. **`src.utilizadores`:**
   - **Pode importar:** `src.shared`.
   - **Proibido importar:** `src.viagens`, `src.faturacao`, `src.estacoes`, `src.manutencao`, `src.relatorios`. (Módulo puramente estável, $C_e = 0$).
3. **`src.faturacao`:**
   - **Pode importar:** `src.utilizadores`, `src.shared`.
   - **Proibido importar:** `src.viagens`, `src.estacoes`, `src.manutencao`, `src.relatorios`. *(Recebe dados da viagem por parâmetro de método; proibido invocar `viagens` para não gerar ciclos).*
4. **`src.estacoes`:**
   - **Pode importar:** `src.manutencao`, `src.shared`.
   - **Proibido importar:** `src.viagens`, `src.faturacao`, `src.utilizadores`, `src.relatorios`.
5. **`src.manutencao`:**
   - **Pode importar:** `src.shared`.
   - **Proibido importar:** qualquer outro módulo de domínio.
6. **`src.relatorios`:**
   - **Pode importar:** `src.viagens`, `src.shared`.
   - **Proibido importar:** `src.faturacao`, `src.manutencao`, `src.estacoes`, `src.utilizadores`.
7. **`src.shared`:**
   - **Proibido importar:** qualquer módulo de domínio em `src/` (camada de suporte folha).

---

## 3. Top 3 Características Arquiteturais e Implicações para o Código

As três características prioritárias conduzem as seguintes decisões no código-fonte (ADR-001):

### A. Disponibilidade (Tolerância a Falhas de Rede)
* **Requisito Operacional:** As docas funcionam offline e acumulam eventos até 24 horas;
* **Implicação para o Código:**
  * O código da doca (simulada) e do servidor deve implementar proteção contra reenvios e duplicados (**US-3**);
  * Toda a viagem recuperada diferida deve ser acompanhada por um identificador determinístico de idempotência:  
    `hash = SHA-256(f"{doca_id}:{bicicleta_id}:{timestamp_inicio}")`;
  * O componente `GestaoViagens` deve verificar se o hash já foi processado antes de criar registos de viagem ou acionar cobranças. Se repetido, descarta a submissão de forma idempotente sem lançar erro de paragem.

### B. Elasticidade a Pedido (Picos de Procura em Eventos)
* **Requisito Operacional:** Picos com 4x a carga normal e 70% dos acessos concentrados em janelas de ponta (8h00–9h30 e 17h30–19h00);
* **Implicação para o Código:**
  * O caminho crítico do desbloqueio (`validar_passe -> destrancar`) deve ter complexidade computacional $O(1)$ em memória ou consulta rápida indexada em SQLite;
  * Não colocar operações pesadas de I/O, processamento em lote ou geração de relatórios síncronas na thread de desbloqueio;
  * O tempo total de execução da função de desbloqueio deve respeitar latência inferior a 2,0 segundos no percentil p95.

### C. Privacidade (Conformidade estrita com o RGPD)
* **Requisito Operacional:** Trajetórias georreferenciadas (telemetria a cada 30 s) são dados pessoais;
* **Implicação para o Código:**
  * **Dissociação Estrutural:** É estritamente proibido criar colunas ou chaves estrangeiras que liguem diretamente tabelas de percurso GPS (`coordenadas_gps`) a tabelas de identificação de utilizador (`nif`, `nome`, `email`, `cartao_navegante`);
  * O histórico de percurso utiliza identificadores anónimos de sessão;
  * O componente `RelatoriosMunicipais` só pode consumir dados agregados por freguesia (contagens e $CO_2$ evitado), sendo proibido expor ou devolver coordenadas brutas por utilizador.

---

## 4. Acoplamento Temporal e Unidades de Trabalho

O código gerado deve respeitar escrupulosamente a ordem temporal e os limites transacionais das operações de negócio:

### 1. Invariante de Ordem (Sequência Obrigatória)
* **Fluxo de Desbloqueio (Início da US-1):**
  1. `ContaUtilizador.validar_permissao_desbloqueio(utilizador_id)` tem de ser executado **obrigatoriamente antes** de emitir o comando de abertura física da tranca.
  2. É proibido destrancar uma bicicleta e validar a subscrição a posteriori. Se a validação falhar, a tranca permanece mecânica e logicamente bloqueada.

### 2. Invariante de Transação (Unidade Atómica de Trabalho)
* **Fluxo de Devolução e Encaixe (Fecho da US-1):**
  * Na receção do sinal de encaixe mecânico da bicicleta na doca, duas operações têm de ocorrer **na mesma unidade de trabalho atómica (transação SQLite)**:
    1. Fecho do registo ativo em `GestaoViagens` (gravação do `timestamp_fim`, cálculo da `duracao_minutos` e mudança de estado para `CONCLUIDA`);
    2. Atualização do estado da doca de `OCUPADA` para `LIVRE` e da bicicleta para `DISPONIVEL` em `MonitorizacaoEstacoes`.
  * Se uma operação falhar, a transação deve sofrer *rollback* integral para impedir inconsistências físicas (bicicleta encaixada mas viagem a continuar a contar tempo, ou doca livre com viagem aberta).
* **Cobrança Desacoplada:**  
  * A notificação de conclusão para `FaturacaoEPagamentos` ocorre logo após a transação mecânica de devolução ser bem-sucedida, não bloqueando a abertura imediata da doca para outros utilizadores.

---

## 5. Convenções de Código e Lista de Proibições para a IA

### 5.1. Convenções Técnicas
* **Python:** Versão 3.11+.
* **Tipagem:** Utilização obrigatória de *type hints* em todas as assinaturas de funções e métodos (`typing.Optional`, `typing.List`, `dataclass`, etc.).
* **Erros de Domínio:** Criar e usar exceções tipadas herdando de `Exception` centralizadas em `src.shared.exceptions` (ex.: `DocaIndisponivelError`, `PasseInvalidoError`, `ViagemDuplicadaError`).
* **Persistência:** Utilizar SQLite através da interface em `src.shared.db`, suportando modo em memória (`:memory:`) para testes rápidos e ficheiro local para execução CLI.
* **Simuladores:** Periféricos de IoT (docas mecânicas) e sistemas externos (Gateway de Pagamento, Autoridade Tributária) devem ser implementados como classes em Python sob `src.shared.simuladores` ou no módulo respetivo.

### 5.2. O que a IA NÃO PODE FAZER 

1. **Não criar importações circulares nem usar *lazy imports* (imports dentro de métodos/funções)** para contornar verificações do `import-linter`.
2. **Não violar a matriz *allowed-to-use* do ADR-007.** Módulos como `faturacao` e `utilizadores` não podem importar `viagens`.
3. **Não aceder diretamente à base de dados fora do módulo `src.shared`** nem partilhar cursores SQL diretamente entre módulos de domínio distintos.
4. **Não violar a Lei de Deméter:**
   * `GestaoViagens` não deve consultar `GestaoTarifarios` nem invocar gateways de pagamento. Deve passar apenas o sumário da viagem (`viagem_id`, `utilizador_id`, `duracao_minutos`) a `FaturacaoEPagamentos`.
   * `GestaoViagens` não deve inspecionar campos internos de `ContaUtilizador`; limita-se a invocar `validar_permissao_desbloqueio()`.
5. **Não duplicar a lógica de cálculo de hash SHA-256.** O cálculo da chave de idempotência deve consumir obrigatoriamente a função partilhada em `src.shared.hash_utils`.
6. **Não fazer chamadas reais a APIs de rede externas (HTTP/sockets)**. Todo o ambiente de periféricos e pagamentos deve ser resolvido por simulação determinística.
7. **Não utilizar variáveis globais mutáveis** para partilha de estado entre componentes.
8. **Não cruzar dados de identidade pessoal com tabelas de percurso GPS.**

---

## 6. Rastreabilidade de Decisões Arquiteturais (ADRs por Componente)

Ao gerar ou alterar código de qualquer componente, os seguintes ADRs devem ser consultados como justificação técnica de referência:

| Pacote / Componente | ADRs Relevantes | Decisão Crítica Associada |
| :--- | :--- | :--- |
| **`src/viagens/`** (`GestaoViagens`, `SincronizacaoDocas`) | ADR-001, ADR-002, ADR-003, ADR-004, ADR-007 | Coesão funcional, mitigação de CoA via SHA-256 (US-3), fluxo unidirecional para faturação sem ciclo. |
| **`src/utilizadores/`** (`ContaUtilizador`) | ADR-002, ADR-003, ADR-007 | Isolamento como componente puramente estável ($C_e = 0$, $I = 0{,}00$). |
| **`src/estacoes/`** (`MonitorizacaoEstacoes`, `RedistribuicaoFrota`) | ADR-001, ADR-002, ADR-007 | Gestão de estados de docas, reporte para manutenção, sem dependência reversa em viagens. |
| **`src/faturacao/`** (`FaturacaoEPagamentos`, `GestaoTarifarios`) | ADR-001, ADR-002, ADR-003, ADR-007 | Encapsulamento das regras de tarifário (45 min grátis) e cobrança sem importar viagens. |
| **`src/manutencao/`** (`ManutencaoFrota`) | ADR-002, ADR-007 | Módulo de suporte autónomo para gestão de ordens de trabalho técnicas. |
| **`src/relatorios/`** (`RelatoriosMunicipais`) | ADR-001, ADR-002, ADR-007 | Agregação estatística por freguesia (US-4) e garantia de privacidade RGPD. |
| **`src/shared/`** (DB, DTOs, Utilitários) | ADR-004, ADR-005, ADR-007 | Conexão relacional, hash único de idempotência e base para as *fitness functions*. |


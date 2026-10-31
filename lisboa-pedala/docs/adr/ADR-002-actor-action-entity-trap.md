# ADR-002: Identificação dos Componentes Lógicos via Actor/Action e Prevenção da Entity Trap

* **Data:** 2026-10-29
* **Estado:** Aceite

## Contexto

Ao delimitar os componentes lógicos do sistema *Lisboa Pedala*, existia o risco de cair no antipadrão da *Entity Trap* (criar componentes mapeados 1-para-1 com tabelas de base de dados e usar sufixos genéricos/ambíguos como `BicicletaManager` ou `ViagemController`).

## Decisão

Adotar a **abordagem Actor/Action** para identificar os componentes lógicos, agrupando o código por **funções e papéis de negócio**:

* Mapear as ações de cada ator (Assinante, Ocasional, Técnico, Carrinha, Gestor Municipal e Sistema) em 9 componentes funcionais: `GestaoViagens`, `ContaUtilizador`, `MonitorizacaoEstacoes`, `FaturacaoEPagamentos`, `GestaoTarifarios`, `ManutencaoFrota`, `RedistribuicaoFrota`, `RelatoriosMunicipais` e `SincronizacaoDocas`.
* Rejeitar nomenclaturas focadas em tabelas de dados.

## Alternativas Rejeitadas

* **Mapeamento 1-para-1 com Entidades de BD (*Entity Trap*):** Rejeitado por agrupar responsabilidades díspares no mesmo componente apenas por partilharem a mesma tabela (ex.: misturar reparação mecânica e alugueres na entidade `Bicicleta`).
* **Abordagem por Workflow:** Rejeitada nesta fase por o sistema possuir múltiplos atores com fluxos independentes e não um único processo sequencial linear.

## Consequências

* **Vantagens:** Limites de componentes claros, elevada coesão funcional e facilidade na atribuição de responsabilidades à equipa (`CODEOWNERS`).
* **Trade-offs / Custos:** Exige definir formalmente regras de importação e permissões de comunicação entre componentes.
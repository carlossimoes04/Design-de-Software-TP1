# ADR-003: Reestruturação do Componente GestaoViagens para Garantia de Coesão Funcional

- **Data:** 2026-10-29
- **Estado:** Aceite

## Contexto

A versão inicial do componente `GestaoViagens` acumulava a validação do passe, o controlo mecânico da tranca, a contagem do tempo, o cálculo dos tarifários e a emissão de faturas. Ao aplicar o *Teste das Conjunções*, a declaração de responsabilidade falhou por acumular 5 responsabilidades de domínios distintos.

## Decisão

Refatorar o `GestaoViagens` para garantir **Coesão Funcional (Nível 1 na Escala de Constantine)**, mantendo nele **apenas a gestão do ciclo de vida mecânico e temporal da viagem**:

1. **Validação de conta e passe:** Extraída para o componente `ContaUtilizador`.
2. **Cálculo de tarifas, cobrança e faturação:** Extraídos para o componente `FaturacaoEPagamentos`.
3. **`GestaoViagens` (Refatorado):** Fica encarregue exclusivamente de registar o desbloqueio mecânico, acompanhar o tempo do percurso e processar o fecho de encaixe na devolução.

## Alternativas Rejeitadas

- **Manter a estrutura sobredimensionada inicial:** Rejeitada porque tornava o componente complexo, difícil de testar e fortemente acoplado a sistemas financeiros e de notificação.

## Consequências

- **Vantagens:** O `GestaoViagens` torna-se focado, simples e altamente estável.
- **Trade-offs / Custos:** O processo de devolução passa a exigir comunicação inter-componentes para acionar a validação e cobrança.
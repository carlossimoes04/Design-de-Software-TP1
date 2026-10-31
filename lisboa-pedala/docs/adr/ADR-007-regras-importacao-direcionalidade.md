# ADR-007: Refinamento da Matriz Allowed-to-Use e Eliminação de Ciclos de Dependências

- **Data:** 2026-10-31
- **Estado:** Aceite (Substitui ADR-005)

## Contexto
Na versão inicial do particionamento por domínio (ADR-005), foram identificados três problemas críticos durante a modelação da vista de módulos e a preparação dos contratos para o *import-linter*:
1. **Contradição no fluxo de devolução (US-1):** o módulo `viagens` estava proibido de importar `faturacao`, mas a devolução de uma bicicleta exige notificar o fecho da viagem para apuramento e cobrança de excedentes;
2. **Ciclo de dependências proibido:** a permissão mútua de importação entre `utilizadores` e `faturacao` criava um ciclo bidirecional (`utilizadores` $\leftrightarrow$ `faturacao`), violando o *Acyclic Dependencies Principle* (ADP) e provocando chumbo nas *fitness functions*;
3. **Inconsistência de granularidade:** o componente `RedistribuicaoFrota` surgia como um módulo de topo independente na tabela *Allowed-to-Use*, quando fisicamente pertence ao pacote `src/estacoes/`.

## Decisão
Substituir a matriz de importações anterior por um modelo estritamente acíclico (DAG) e alinhado com as 7 pastas reais em `src/`:
1. **Autorizar `viagens` a importar `faturacao`:** permite que a devolução despolete diretamente a cobrança, mantendo a relação unidirecional (a faturação continua proibida de importar viagens);
2. **Eliminar o ciclo `utilizadores` $\leftrightarrow$ `faturacao`:** retirar a autorização de `utilizadores` importar `faturacao`. O módulo `utilizadores` torna-se puramente estável ($C_e = 0, I = 0,00$), sendo apenas consultado por `faturacao` e `viagens`;
3. **Desacoplamento via Interface:** operações como a consulta de faturas ou a subscrição de passes pelo utilizador passam a ser dirigidas diretamente pela interface (CLI / API REST) ao módulo `faturacao`, sem passar por `utilizadores` como intermediário;
4. **Consolidação de Módulos:** tratar a dependência entre `RedistribuicaoFrota` e `MonitorizacaoEstacoes` como interna ao pacote `src/estacoes/`, fixando a tabela *Allowed-to-Use* exatamente nos 7 pacotes de código.

## Alternativas Rejeitadas
- **Manter chamadas bidirecionais com importações locais (*lazy imports*):** rejeitado por violar o ADP, fragilizar a arquitetura em tempo de execução e falhar na validação estática do *import-linter*;
- **Desacoplar totalmente `viagens` de `faturacao` via orquestrador externo:** rejeitado para evitar complexidade desnecessária na CLI e garantir que a unidade de trabalho da devolução é concluída de ponta a ponta pelo backend.

## Consequências
- **Vantagens:** grafo de dependências transformado num Grafo Acíclico Dirigido (DAG), eliminação de riscos de *circular import* no Python e garantia de validação limpa nas *fitness functions*. As métricas aferentes e eferentes ficam balanceadas ($\sum C_a = \sum C_e = 9$).
- **Trade-offs / Custos:** o módulo `viagens` passa a ter um acoplamento eferente adicional ($C_e = 3$).
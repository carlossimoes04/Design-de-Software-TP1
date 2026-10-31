# ADR-005: Particionamento de Topo por Domínio e Validação com Fitness Functions

- **Data:** 2026-10-30
- **Estado:** Revisto (substituído pelo ADR-007)

## Contexto

Era necessário decidir a organização da raiz do código-fonte (`src/`) no repositório Python 3.11 e definir a forma de proibir dependências circulares e violações de arquitetura durante o desenvolvimento da equipa.

## Decisão

1. **Particionamento por Domínio:** organizar a pasta `src/` pelas áreas de negócio do sistema (`viagens`, `utilizadores`, `estacoes`, `faturacao`, `manutencao`, `relatorios` e `shared`);
2. **Governação Automatizada via Fitness Functions:** adotar a ferramenta `import-linter` em `tests/architecture/` com regras formais no ficheiro `.importlinter` para validar automaticamente a matriz *allowed-to-use* e a ausência de ciclos em integração contínua (CI).

## Alternativas Rejeitadas

- **Particionamento Técnico por Camadas (`controllers/`, `services/`, `repositories/`):** rejeitado porque espalha a lógica de um mesmo conceito de negócio por múltiplos diretórios, aumentando a complexidade de manutenção;
- **Verificação Manual de Código (*Code Review*):** rejeitada por não garantir a deteção sistemática de importações circulares à medida que a base de código cresce.

## Consequências

- **Vantagens:** elevada coesão por pasta, autonomia de trabalho entre os elementos da equipa (`CODEOWNERS`) e deteção automática de erros de arquitetura no *build*;
- **Trade-offs / Custos:** alterações técnicas transversais afetam múltiplos pacotes; exige guardar utilitários genéricos na pasta `src/shared/`.

***Nota de Revisão* (2026-10-31):** as regras iniciais de importação deste ADR originavam um ciclo bidirecional entre utilizadores e faturação e impediam a notificação de viagens para cobrança. Estas regras foram revistas e substituídas pelo ADR-007.
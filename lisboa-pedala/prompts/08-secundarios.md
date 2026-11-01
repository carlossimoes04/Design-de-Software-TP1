# Registo de Geração com IA: Componentes Secundários

- **Data:** 2026-11-01
- **Componentes:** `src.manutencao.manutencao_frota` e `src.estacoes.redistribuicao_frota`
- **Ficheiros de Contexto Fornecidos:**
  - `ARCHITECTURE.md` (Secção 1: Papel dos Componentes; Secção 2: Regras Allowed-to-Use; Secção 4: Acoplamento Temporal)
  - `docs/02-componentes.md` (Secção 4.1: Métricas de Acoplamento Ce e Ca; Secção 5.1: Conascência de Significado)
  - `docs/03-particionamento-e-vistas.md` (Secção 2.1: Papel dos Módulos; Secção 2.2: Tabela Allowed-to-Use; Secção 4.2: Responsabilidade do Aluno 2 no CODEOWNERS)
  - `docs/adr/ADR-007-regras-importacao-direcionalidade.md` (Decisão 4: Consolidação de RedistribuicaoFrota em estacoes)
- **Ferramenta / Modelo de IA:** Antigravity (Gemini 3.8 Flash High)
- **Estado:** **ACEITE**

---

## 1. Pedido Feito à IA (Prompt)

```text
Atuando como engenheiro de software, implementa os 2 componentes secundários em falta para completar os 9 componentes lógicos do sistema Lisboa Pedala (Python 3.11), com base estrita no ARCHITECTURE.md, no ADR-007, no docs/02-componentes.md e no docs/03-particionamento-e-vistas.md:

1. `src/manutencao/manutencao_frota.py` (Componente ManutencaoFrota - Aluno 2):
   - Conforme o docs/02-componentes.md (4.1), o módulo é puramente estável (Ce = 0, I = 0.00);
   - Conforme o docs/02-componentes.md (5.1), respeita a conascência de significado com as estações quanto ao estado das bicicletas ('LIVRE', 'AVARIADA', 'EM_MANUTENCAO');
   - Responsabilidade: Gestão de ordens de trabalho de reparação para os 25 técnicos municipais (abrir ordem, listar pendentes, concluir ordem);
   - Contrato estrito (Contrato 3 do .importlinter): Proibido importar qualquer módulo de domínio; apenas usa `src.shared`.

2. `src/estacoes/redistribuicao_frota.py` (Componente RedistribuicaoFrota - Aluno 2):
   - Conforme a Decisão 4 do ADR-007, reside no pacote `src/estacoes/` e depende internamente de `MonitorizacaoEstacoes` (Ce = 1, I = 1.00);
   - Responsabilidade: Algoritmo de sugestão de rotas de equilíbrio para as 6 carrinhas municipais (Requisito 6 do enunciado);
   - Lê ocupação de docas através de `MonitorizacaoEstacoes` e deteta estações críticas com ocupação <= 20% (abastecer) ou >= 80% (recolher bicicletas excedentárias);
   - Contrato estrito (Contrato 4 do .importlinter): Proibido acoplar a `viagens`, `faturacao` ou `utilizadores`.
```

---

## 2. Resultado da Geração (Aceite e Porquê)

- **Resultado:** **Aceite na totalidade à 1.ª tentativa**.
- **Justificação:**
  1. **Completude Integral dos 9 Componentes:** Todos os 9 componentes lógicos da especificação passam a ter código funcional em Python 3.11;
  2. **Estabilidade Pura em Manutenção ($C_e = 0$):** `ManutencaoFrota` gere o ciclo de vida das ordens de trabalho de forma isolada, comunicando unicamente com o SQLite em `src.shared` em estrita conformidade com o Contrato 3 do `.importlinter`;
  3. **Mitigação de Conascência de Significado:** Os estados das bicicletas e ordens alinham-se rigorosamente com os enums definidos em `src.shared.models` (`EstadoDoca`), cumprindo a análise da Secção 5.1 do `02-componentes.md`;
  4. **Coesão em Estações ($C_e = 1$):** `RedistribuicaoFrota` funciona como consumidor direto de `MonitorizacaoEstacoes` dentro da mesma pasta de domínio (`src/estacoes/`), cumprindo a Decisão 4 do **ADR-007** e evitando dependências transversais desnecessárias.

---

## 3. Avaliação com as *Fitness Functions*

Execução de `pytest tests/architecture/`:

```text
=============
Import Linter
=============

---------
Contracts
---------

Analyzed 22 files, 13 dependencies.
-----------------------------------

Shared nao pode importar modulos de dominio KEPT
Utilizadores nao pode importar outros dominios KEPT
Manutencao nao pode importar outros dominios KEPT
Estacoes so pode importar manutencao e shared KEPT
Faturacao nao pode importar viagens nem estacoes KEPT
Viagens nao pode importar manutencao nem relatorios KEPT
Relatorios nao pode importar estacoes faturacao utilizadores ou manutencao KEPT

Contracts: 7 kept, 0 broken.

============================== 1 passed in 0.48s ==============================
```

- **Houve violação da arquitetura?** Não. Todas as 13 dependências do sistema respeitam as regras *Allowed-to-Use* e preservam o grafo estritamente acíclico (DAG).
# Registo de Geração com IA: Pacote `src.faturacao` (Tentativa 1)

- **Data:** 2026-11-01
- **Componentes:** `src.faturacao.gestao_tarifarios` e `src.faturacao.faturacao_pagamentos`
- **Ficheiros de Contexto Fornecidos:**
  - `ARCHITECTURE.md` (Secção 1: Papel dos Componentes; Secção 2: Regras Allowed-to-Use; Secção 4: Acoplamento Temporal)
  - `docs/adr/ADR-007-regras-importacao-direcionalidade.md`
- **Ferramenta / Modelo de IA:** Antigravity (Gemini 3.8 Flash High)
- **Estado:** **ACEITE**

---

## 1. Pedido Feito à IA (Prompt)

```text
Atuando como engenheiro de software, implementa os componentes GestaoTarifarios e FaturacaoEPagamentos no pacote `src/faturacao/` para o sistema Lisboa Pedala (Python 3.11), com base no ARCHITECTURE.md e no ADR-007.

Responsabilidades dos Componentes:
- `gestao_tarifarios.py`: Calcular custos de viagens (US-1: primeiros 45 min grátis para passes anuais e cobrança por blocos de 15 min a 0.50€; ocasionais com taxa base de 1.50€ + 0.15€/min);
- `faturacao_pagamentos.py`: Receber o identificador de uma viagem terminada (`viagem_id`), consultar os dados da viagem, processar a cobrança via SimuladorPagamentos e emitir a fatura na base de dados SQLite.

Restrições:
- Utiliza a base de dados SQLite e DTOs via `src.shared`.
```

---

## 2. Verificação com *Fitness Functions* (Resultado da Execução)

Execução do comando `pytest tests/architecture/`:

```text
=================================== FAILURES ===================================
____________________ test_fitness_functions_allowed_to_use _____________________

    def test_fitness_functions_allowed_to_use():
>       assert result.returncode == 0, f"Violação da arquitetura detetada:\n{result.stdout}\n{result.stderr}"
E       AssertionError: Violação da arquitetura detetada:
E         =============
E         Import Linter
E         =============
E         
E         ---------
E         Contracts
E         ---------
E         
E         Analyzed 22 files, 10 dependencies.
E         -----------------------------------
E         
E         Shared nao pode importar modulos de dominio KEPT
E         Utilizadores nao pode importar outros dominios KEPT
E         Manutencao nao pode importar outros dominios KEPT
E         Estacoes so pode importar manutencao e shared KEPT
E         Faturacao nao pode importar viagens nem estacoes BROKEN
E         Viagens nao pode importar manutencao nem relatorios KEPT
E         Relatorios nao pode importar estacoes faturacao utilizadores ou manutencao KEPT
E         
E         Contracts: 6 kept, 1 broken.
E         
E         ----------------
E         Broken contracts
E         ----------------
E         
E         Faturacao nao pode importar viagens nem estacoes
E         ------------------------------------------------
E         
E         src.faturacao is not allowed to import src.viagens:
E         
E         -   src.faturacao.faturacao_pagamentos -> src.viagens.gestao_viagens (l.15)
```

---

## 3. Decisão da Equipa: REJEITADO

- **Motivo da Rejeição:**  
  O código gerado viola frontalmente o **Contrato 5** do `.importlinter` e a **Decisão 1 do ADR-007**.  
  Ao importar `src.viagens`, o módulo `faturacao` cria uma dependência cíclica bidirecional (`viagens` $\leftrightarrow$ `faturacao`), destruindo a topologia de Grafo Acíclico Dirigido (DAG).
- **Ação:**  
  Código rejeitado. Conforme estipulado no ADR-007, a faturação não pode ir buscar a viagem; tem de **receber os dados da viagem por parâmetro de método (`ViagemDTO`)**, mantendo a relação estritamente unidirecional a partir de `viagens`.

  ---

## 4. Pedido de Correção à IA (Prompt Refinado - Tentativa 2)

```text
Atuando como engenheiro de software, corrige a implementação do componente FaturacaoEPagamentos em `src/faturacao/faturacao_pagamentos.py` para o sistema Lisboa Pedala (Python 3.11).

Problema da Tentativa 1:
A versão anterior violou a arquitetura (Contrato 5 do .importlinter) ao importar `src.viagens.gestao_viagens`. Conforme o ADR-007, a faturação não pode importar viagens (evitando o ciclo bidirecional). A faturação deve receber os dados da viagem fechada por parâmetro de método (`viagem: ViagemDTO`), mantendo a relação estritamente unidirecional a partir de viagens.

Responsabilidades Estritas de FaturacaoEPagamentos:
- Método `processar_fecho_viagem(viagem: ViagemDTO, tipo_passe: TipoPasse) -> tuple[float, FaturaDTO]`:
  1. Invoca `GestaoTarifarios` para calcular o custo exato da viagem com base na duração e no tarifário;
  2. Processa o débito através do `SimuladorPagamentos`;
  3. Grava a fatura fiscal na base de dados SQLite (retenção legal);
  4. Devolve o custo apurado e o objeto `FaturaDTO`.
- Método `listar_faturas_por_nif(nif: str) -> List[FaturaDTO]`.

Restrições Arquiteturais Rígidas:
- REMOVER qualquer importação de `src.viagens`, `src.estacoes`, `src.manutencao` ou `src.relatorios`;
- Importar apenas `src.faturacao.gestao_tarifarios` e `src.shared` (db, models, simuladores).
```

---

## 5. Verificação com *Fitness Functions* após Correção

Execução de `pytest tests/architecture/`:

```text
=============
Import Linter
=============

---------
Contracts
---------

Analyzed 22 files, 8 dependencies.
----------------------------------

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

---

## 6. Decisão Final da Equipa: ACEITE

- **Resultado:** **Aceite na totalidade**.
- **Justificação:**  
  A relação acíclica exigida pelo **ADR-007** e pelo Contrato 5 foi restabelecida. O módulo `viagens` pode notificar `faturacao`, mas a faturação opera de forma autónoma sem conhecer a implementação de viagens, mantendo o Grafo Acíclico Dirigido (DAG) 100% verde.
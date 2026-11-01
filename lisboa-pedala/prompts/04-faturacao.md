# Registo de Geração com IA: Pacote `src.faturacao` (Tentativa 1)

- **Data:** 2026-11-01
- **Componentes:** `src.faturacao.gestao_tarifarios` e `src.faturacao.faturacao_pagamentos`
- **Ficheiros de Contexto Fornecidos:**
  - `ARCHITECTURE.md` (Secção 1: Papel dos Componentes; Secção 2: Regras Allowed-to-Use; Secção 4: Acoplamento Temporal)
  - `docs/adr/ADR-007-regras-importacao-direcionalidade.md`
- **Ferramenta / Modelo de IA:** Antigravity (Gemini 3.8 Flash High)
- **Estado:** **REJEITADO (Violação Arquitetural)**

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
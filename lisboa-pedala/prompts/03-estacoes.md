# Registo de Geração com IA: Componente `MonitorizacaoEstacoes` (Tentativa 1)

- **Data:** 2026-11-01
- **Componente:** `src.estacoes.monitorizacao_estacoes`
- **Ficheiros de Contexto Fornecidos:**
  - `ARCHITECTURE.md` (Secção 1: Papel dos Componentes; Secção 2: Regras Allowed-to-Use)
  - `docs/adr/ADR-007-regras-importacao-direcionalidade.md`
- **Ferramenta / Modelo de IA:** Antigravity (Gemini 3.8 Flash High)
- **Estado:** **ACEITE**

---

## 1. Pedido Feito à IA (Prompt)

```text
Atuando como engenheiro de software, implementa o componente MonitorizacaoEstacoes em `src/estacoes/monitorizacao_estacoes.py` para o sistema Lisboa Pedala (Python 3.11), com base no ARCHITECTURE.md e no ADR-007.

Responsabilidades do Componente:
- Consultar estações e inventário de docas livres/ocupadas (US-1 e US-4);
- Destrancar bicicleta numa doca para início de viagem, validando antes se o utilizador que está a pedir tem passe válido;
- Trancar e receber bicicleta numa doca livre no fecho de viagem.

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
E         Analyzed 22 files, 9 dependencies.
E         ----------------------------------
E         
E         Shared nao pode importar modulos de dominio KEPT
E         Utilizadores nao pode importar outros dominios KEPT
E         Manutencao nao pode importar outros dominios KEPT
E         Estacoes so pode importar manutencao e shared BROKEN
E         Faturacao nao pode importar viagens nem estacoes KEPT
E         Viagens nao pode importar manutencao nem relatorios KEPT
E         Relatorios nao pode importar estacoes faturacao utilizadores ou manutencao KEPT
E         
E         Contracts: 6 kept, 1 broken.
E         
E         ----------------
E         Broken contracts
E         ----------------
E         
E         Estacoes so pode importar manutencao e shared
E         --------------------------------------------
E         
E         src.estacoes is not allowed to import src.utilizadores:
E         
E         -   src.estacoes.monitorizacao_estacoes -> src.utilizadores.conta_utilizador (l.12)
```

---

## 3. Decisão da Equipa: REJEITADO

- **Motivo da Rejeição:**  
  O código gerado quebrou o **Contrato 4** do `.importlinter` e violou as regras *Allowed-to-Use* do **ADR-007**. O módulo `estacoes` só tem autorização para importar `manutencao` e `shared`.  
  A validação da conta/passe do utilizador é uma responsabilidade de negócio que cabe exclusivamente ao orquestrador `viagens`, e não ao gestor físico das docas.
- **Ação:**  
  Código rejeitado. O prompt tem de ser corrigido para remover a verificação de contas do módulo de estações, mantendo o método de destrancamento focado estritamente na gestão da doca e do inventário.

---

## 4. Pedido de Correção à IA (Prompt Refinado - Tentativa 2)

```text
Atuando como engenheiro de software, corrige a implementação do componente MonitorizacaoEstacoes em `src/estacoes/monitorizacao_estacoes.py` para o sistema Lisboa Pedala (Python 3.11).

Problema da Tentativa 1:
A versão anterior violou a arquitetura (Contrato 4 do .importlinter) ao importar `src.utilizadores.conta_utilizador`. Conforme o ADR-007, o módulo `estacoes` só pode importar `manutencao` e `shared`. A validação da conta e do passe do utilizador é da responsabilidade exclusiva do orquestrador `viagens`.

Responsabilidades Estritas de MonitorizacaoEstacoes:
- Consultar estações e inventário de docas livres/ocupadas;
- Destrancar bicicleta numa doca (marcando-a como LIVRE e acionando o SimuladorDoca);
- Trancar e receber bicicleta numa doca livre (marcando-a como OCUPADA e acionando o SimuladorDoca).

Restrições Arquiteturais Rígidas:
- REMOVER qualquer importação de `src.utilizadores`, `src.faturacao` ou `src.viagens`;
- Acoplar EXCLUSIVAMENTE a `src.shared` (db, models, simuladores).
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

============================== 1 passed in 0.47s ==============================
```

---

## 6. Decisão Final da Equipa: ACEITE

- **Resultado:** **Aceite na totalidade**.
- **Justificação:**  
  A segregação de responsabilidades foi reposta: o módulo `estacoes` passa a gerir apenas docas e estações físicas, em conformidade estrita com o Contrato 4 e o **ADR-007**. Todos os 7 contratos do `import-linter` foram validados a verde.
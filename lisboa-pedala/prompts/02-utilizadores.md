# Registo de Geração com IA: Componente `ContaUtilizador` (Tentativa 2)

- **Data:** 2026-11-01
- **Componente:** `src.utilizadores.conta_utilizador`
- **Ficheiros de Contexto Fornecidos:**
  - `ARCHITECTURE.md` (Secção 1: Papel dos Componentes; Secção 2: Regras Allowed-to-Use)
  - `docs/adr/ADR-007-regras-importacao-direcionalidade.md`
- **Ferramenta / Modelo de IA:** Antigravity (Gemini 3.8 Flash High)
- **Estado:** **Aceite**

---

## 1. Pedido Feito à IA (Prompt)

```text
Atuando como engenheiro de software, implementa o componente ContaUtilizador em `src/utilizadores/conta_utilizador.py` para o sistema Lisboa Pedala (Python 3.11), com base no ARCHITECTURE.md e no ADR-007.

Responsabilidades do Componente:
- Obter dados do utilizador por ID ou NIF;
- Validar se o utilizador tem passe anual ativo ou saldo suficiente para desbloqueio (US-1);
- Atualizar saldo na base de dados SQLite;
- Permitir consultar o histórico de faturas emitidas para o utilizador.

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
E         Utilizadores nao pode importar outros dominios BROKEN
E         Manutencao nao pode importar outros dominios KEPT
E         Estacoes so pode importar manutencao e shared KEPT
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
E         Utilizadores nao pode importar outros dominios
E         ----------------------------------------------
E         
E         src.utilizadores is not allowed to import src.faturacao:
E         
E         -   src.utilizadores.conta_utilizador -> src.faturacao.faturacao_pagamentos (l.10)
```

---

## 3. Decisão da Equipa: REJEITADO

- **Motivo da Rejeição:**  
  O código gerado viola o **Contrato 2** do `.importlinter` e a decisão central do **ADR-007**. O módulo `utilizadores` deve ter acoplamento eferente nulo ($C_e = 0$, puramente estável). Ao importar `faturacao`, cria um acoplamento proibido e um potencial ciclo de dependências.
- **Ação:**  
  O código não pode entrar na versão final. É necessário refazer o prompt, retirando a responsabilidade de consulta de faturas de `ContaUtilizador` e forçando a independência total em relação a outros domínios de negócio.

---

## 4. Pedido de Correção à IA (Prompt Refinado - Tentativa 2)

```text
Atuando como engenheiro de software, corrige a implementação do componente ContaUtilizador em `src/utilizadores/conta_utilizador.py` para o sistema Lisboa Pedala (Python 3.11).

Problema da Tentativa 1:
A versão anterior violou a arquitetura (Contrato 2 do .importlinter) ao importar `src.faturacao.faturacao_pagamentos`. Conforme o ADR-007, o módulo `utilizadores` é puramente estável (Ce = 0) e não pode importar faturação nem nenhum outro módulo de negócio. A consulta de histórico de faturas pertence à interface (CLI) comunicando diretamente com o módulo `faturacao`.

Responsabilidades Estritas de ContaUtilizador:
- Obter utilizador por ID ou NIF;
- Validar elegibilidade de desbloqueio para a US-1 (passe anual ativo para assinantes ou saldo >= 2.00€ para ocasionais);
- Atualizar saldo na base de dados SQLite.

Restrições Arquiteturais Rígidas:
- REMOVER qualquer importação de `src.faturacao` ou de outro módulo de domínio;
- Acoplar EXCLUSIVAMENTE a `src.shared` (db e models).
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
============================== 1 passed in 0.38s ==============================
```
---
## 6. Decisão Final da Equipa: ACEITE
- **Resultado:** **Aceite na totalidade**.
- **Justificação:**  
  A remoção da dependência indevida repôs a estabilidade arquitetural de `utilizadores` ($C_e = 0, I = 0{,}00$), conforme definido no **ADR-007**. O código cumpre todos os requisitos funcionais para a US-1 e passa com 100% de conformidade nas *fitness functions*.
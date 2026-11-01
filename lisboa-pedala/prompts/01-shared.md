# Registo de Geração com IA: Pacote `src.shared`

- **Data:** 2026-11-01
- **Componente / Pacote:** `src.shared` (`db.py`, `models.py`, `hash_utils.py`, `simuladores.py`)
- **Ferramenta / Modelo de IA:** Antigravity (Gemini 3.8 Flash High)
- **Estado:** Aceite na totalidade

---

## 1. Pedido Feito (Prompt) e Ficheiros de Contexto

### Ficheiros de Contexto Fornecidos:
- `ARCHITECTURE.md` (Secção 1: Identificação dos Componentes; Secção 2: Regras Allowed-to-Use; Secção 3.A: Disponibilidade e Idempotência; Secção 3.C: Privacidade RGPD);
- `docs/03-particionamento-e-vistas.md` (Secção 2.2: Tabela Allowed-to-Use; Secção 3.1: Componentes e Conectores; Secção 4.1: Mapeamento Físico SQLite);
- `docs/adr/ADR-001-top3-caracteristicas.md`;
- `docs/adr/ADR-007-regras-importacao-direcionalidade.md`.

### Prompt Enviado à IA:
```text
Atuando como engenheiro de software, gera a camada de suporte partilhada em `src/shared/` para o protótipo Lisboa Pedala (Python 3.11), com base estrita no ARCHITECTURE.md e no ADR-007.

A camada é composta por 5 ficheiros:
1. `models.py`: DTOs (dataclass) para transporte de dados sem acoplamento de negócio (UtilizadorDTO, EstacaoDTO, DocaDTO, BicicletaDTO, ViagemDTO, FaturaDTO, EventoDocaOfflineDTO, RelatorioFreguesiaDTO).
2. `hash_utils.py`: Função `gerar_hash_viagem(doca_id, bicicleta_id, timestamp_inicio)` calculando o hash determinístico SHA-256 conforme a secção 3.A do ARCHITECTURE.md.
3. `simuladores.py`: Classes `SimuladorDoca` (destrancar, trancar e simular acumulação offline de 24h) e `SimuladorPagamentos` (autorizações de MB WAY e Cartão sem APIs reais externas).
4. `db.py`: Conexão SQLite (`lisboa_pedala.db`), script DDL `init_db()` com CREATE TABLE IF NOT EXISTS e `seed_dados_iniciais()` com dados fictícios para Lisboa (US-1 e US-4).
5. `__init__.py`: Fachada pública do pacote que reexporta os símbolos principais (`__all__`), permitindo importações diretas e limpas a partir de `src.shared`.

Restrições Arquiteturais Rígidas (Mandatórias):
- Conforme o ADR-007 e o Contrato 1 do .importlinter, o pacote `src.shared` é uma camada folha base e ESTÁ ESTRITAMENTE PROIBIDO de importar qualquer módulo de domínio (`viagens`, `estacoes`, `faturacao`, `utilizadores`, `manutencao`, `relatorios`). Usa apenas a standard library do Python.
- Conforme a Secção 3.C do ARCHITECTURE.md (Privacidade RGPD), é expressamente proibido ligar diretamente identificadores de utilizadores (NIF/nome) com tabelas de coordenadas geográficas.
```

---

## 2. Resultado da Geração (Aceite ou Rejeitado e Porquê)

- **Resultado:** **Aceite**.
- **Justificação:**
  1. **Independência Estrita:** Todos os ficheiros usam exclusivamente módulos embutidos do Python (`sqlite3`, `dataclasses`, `hashlib`, `enum`, `typing`). Nenhuma importação de pacotes de domínio foi realizada;
  2. **Isolamento de Persistência:** A base de dados SQLite é gerida centralizadamente em `db.py`, inicializando as 7 tabelas necessárias com chave primária e restrições de integridade referencial;
  3. **Conformidade com Requisitos Operacionais:** 
     - A fórmula `SHA-256(f"{doca_id}:{bicicleta_id}:{timestamp_inicio}")` foi implementada exatamente como prescrito no ADR-001/ARCHITECTURE.md;
     - Os simuladores fornecem os métodos necessários para testar as User Stories (US-1 e US-3) sem necessidade de infraestrutura externa.

---

## 3. Avaliação de Violações da Arquitetura

- **Houve violação da arquitetura?** Não. O código gerado cumpriu todas as restrições arquiteturais à primeira tentativa.
- **Validação com as *Fitness Functions*:**
  O teste `tests/architecture/test_architecture.py` executou o `import-linter` sobre o repositório após a criação dos 5 ficheiros, validando o **Contrato 1** (`Shared nao pode importar modulos de dominio`):
  ```text
  =============
  Import Linter
  =============

  ---------
  Contracts
  ---------

  Analyzed 22 files, 0 dependencies.
  ----------------------------------

  Shared nao pode importar modulos de dominio KEPT
  Utilizadores nao pode importar outros dominios KEPT
  Manutencao nao pode importar outros dominios KEPT
  Estacoes so pode importar manutencao e shared KEPT
  Faturacao nao pode importar viagens nem estacoes KEPT
  Viagens nao pode importar manutencao nem relatorios KEPT
  Relatorios nao pode importar estacoes faturacao utilizadores ou manutencao KEPT

  Contracts: 7 kept, 0 broken.

  ============================== 1 passed in 0.54s ==============================
  ```
  O linter confirmou $C_e = 0$ para o pacote `src.shared` em relação aos domínios de negócio (apenas dependências internas à standard library).

- **Revisão Humana de Restrições Específicas:**
  1. **Privacidade e RGPD (ADR-001 / ARCHITECTURE.md 3.C):**  
     A revisão manual do esquema DDL em `src/shared/db.py` confirmou a **dissociação estrutural**: não existe nenhuma tabela de telemetria GPS associada ao NIF ou identidade dos utilizadores. A tabela `viagens` referencia apenas os identificadores das docas (`doca_inicio_id`, `doca_fim_id`);
  2. **Garantia de Idempotência (ADR-001 / ARCHITECTURE.md 3.A / US-3):**  
     A revisão confirmou que a tabela `viagens` define uma restrição `UNIQUE` na coluna `hash_idempotencia` e que foi criada a tabela auxiliar `eventos_offline_processados` para suporte ao reenvio de lotes das docas sem duplicação de dados;
  3. **Fachada Pública (`__init__.py`):**  
     Verificado que a lista `__all__` reexporta apenas DTOs e funções utilitárias partilhadas, sem vazar implementações acopladas.
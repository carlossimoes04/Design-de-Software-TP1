# Lisboa Pedala - Trabalho Prático 1
Trabalho prático desenvolvido no âmbito da unidade curricular de **Design de Software (2026/2027)** do **Mestrado em Engenharia Informática** da Faculdade de Ciências da Universidade de Lisboa (FCUL).

---

## Elementos do Grupo e CODEOWNERS

| Nome do Aluno | Número | Utilizador GitHub | Responsabilidade de Domínio (`CODEOWNERS`) |
| :--- | :--- | :--- | :--- |
| **Carlos Simões** | 68017 | @carlossimoes04 | `src/viagens/`, `src/utilizadores/`, `src/relatorios/`, `src/shared/`, `tests` |
| **Joana Ramos** | 68094 | @joanar2004 | `src/faturacao/`, `src/estacoes/`, `src/manutencao/`, `src/shared/`, `tests` |

---

## Utilização de IA
De acordo com a secção 4 do enunciado, declara-se a utilização de ferramentas de GenAI:
- **Ferramenta principal**: Google Antigravity
- **Modelo utilizado**: Gemini 3.8 Flash High
- **Âmbito de utilização**:
    1. **Geração de código e testes**: o código dos 9 componentes em `src/` e os respetivos testes em `tests/` foram gerados através de prompts estruturadas a partir da especificação formal (ARCHITECTURE.md e ADRs);
    2. Violações de arquitetura: foram documentadas com sucesso 3 violações cometidas pela IA (registadas em `prompts/02-utilizadores.md`, `prompts/03-estacoes.md` e `prompts/04-faturacao.md`), todas intercetadas e chumbadas pelas *fitness functions*;
    3. **Revisão**: a IA serviu como revisor de consistência textual da especificação.
- **Autoria**: a seleção das Top-3 características arquiteturais, a decomposição dos componentes por *Actor/Action*, o particionamento por domínio, a matriz *Allowed-to-Use* (DAG) e as decisões documentadas nos 7 ADRs foram concebidas e decididas pelo grupo.

---

## Visão geral do sistema

O **Lisboa Pedala** é um sistema de partilha de bicicletas elétricas para a cidade de Lisboa, concebido sob o estilo de **Monólito Modular** com particionamento de topo por **Domínio de Negócio**.
O protótipo implementa **3 *User Stories***:
* **US-1 (Obrigatória - Desbloqueio e Cobrança):** como assinante ou utilizador ocasional, desbloqueio uma bicicleta e devolvo-a. A viagem é concluída, a duração é calculada, o tarifário é aplicado (primeiros 45 min gratuitos para passes anuais e blocos de 15 min a 0.50€; taxa base de 1.50€ + 0.15€/min para ocasionais) e a fatura fiscal é emitida com NIF (envolve 5 componentes: `GestaoViagens`, `ContaUtilizador`, `MonitorizacaoEstacoes`, `FaturacaoEPagamentos` e `GestaoTarifarios`);
* **US-3 (Tolerância a falhas e idempotência):** como doca física sem rede, armazeno localmente os eventos mecânicos de encaixe/desencaixe e reenvio o lote quando a ligação for restabelecida. O backend assegura a **idempotência**, processando novos eventos e descartando duplicados sem duplicar viagens;
* **US-4 (Relatórios municipais e RGPD):** como gestor da Câmara Municipal de Lisboa, obtenho relatórios agregados de utilização por freguesia, tempo de circulação e estimativa de $CO_2$ evitado, sob dissociação estrutural e anonimização em cumprimento integral do **RGPD** (sem exposição de identidades ou percursos pessoais).

---

## Estrutura do repositório

```text
lisboa-pedala/
├── ARCHITECTURE.md          # Especificação arquitetural para orientar humanos e IA
├── CODEOWNERS               # Mapeamento de responsabilidades por componente
├── .importlinter             # 7 Contratos estritos de governação de dependências (Fitness Functions)
├── docs/
│   ├── 01-caracteristicas.md        # Características arquiteturais
│   ├── 02-componentes.md            # Componentes lógicos via Actor/Action, métricas Ca, Ce, I e conascência
│   ├── 03-particionamento-e-vistas.md # Particionamento por domínio, matriz Allowed-to-Use e vista C&C
│   ├── reflexao.md                  # Relatório crítico de reflexão (2 páginas: IA, violações e linter)
│   ├── adr/                         # 7 Architecture Decision Records (ADR-001 a ADR-007)
│   └── diagramas/                   # Diagramas C4 Model (Níveis 1, 2 e 3) em Mermaid
├── prompts/                         # Registo de prompts e 3 violações de arquitetura documentadas
├── src/                             # Código fonte particionado por domínio (Python 3.11)
│   ├── cli.py                       # Interface interativa de linha de comandos
│   ├── shared/                      # DTOs, base de dados SQLite e simuladores de hardware/pagamentos
│   ├── utilizadores/                # ContaUtilizador (Ce = 0, puramente estável)
│   ├── estacoes/                    # MonitorizacaoEstacoes e RedistribuicaoFrota
│   ├── viagens/                     # GestaoViagens (US-1) e SincronizacaoDocas (US-3)
│   ├── faturacao/                   # GestaoTarifarios e FaturacaoEPagamentos
│   ├── manutencao/                  # ManutencaoFrota (Ce = 0, isolado)
│   └── relatorios/                  # RelatoriosMunicipais (US-4)
└── tests/
    ├── architecture/                # Fitness function automatizada (test_architecture.py)
    ├── test_us1_viagens.py          # Teste funcional de integração da US-1
    ├── test_us3_sincronizacao.py    # Teste funcional de idempotência SHA-256 da US-3
    └── test_us4_relatorios.py       # Teste funcional de conformidade RGPD da US-4
```

---

## Instalação e execução

### 1. Pré-requisitos

* **Python 3.11+** instalado;
* `pip` e ambiente virtual `venv`.

### 2. Configurar o ambiente Virtual

Na raiz do repositório:
```bash
# Criar o ambiente virtual
python -m venv .venv

# Ativar no Linux / macOS:
source .venv/bin/activate

# Ativar no Windows (PowerShell):
.venv\Scripts\Activate.ps1
```

### 3. Instalar dependências

```bash
pip install pytest import-linter
```

---

## Execução dos testes e *fitness functions*

Para validar a integridade da arquitetura (7 contratos) e o funcionamento das 3 *User Stories* num único comando:
```bash
# Entrar na pasta do projeto
cd lisboa-pedala

# Correr todos os testes e fitness functions
pytest -v
```

**O que este comando valida automaticamente:**
> 1. `test_architecture.py`: garante que as 7 regras *Allowed-to-Use* do `.importlinter` se mantêm sem ciclos (`7 kept, 0 broken`);
> 2. `test_us1_viagens.py`: testa o fluxo completo de desbloqueio, devolução e faturação da US-1;
> 3. `test_us3_sincronizacao.py`: testa a tolerância a falhas e a idempotência SHA-256 da doca offline;
> 4. `test_us4_relatorios.py`: testa a agregação municipal de métricas e conformidade com o RGPD.

---

## Demonstração interativa via CLI

O sistema inclui uma interface de linha de comandos para demonstração rápida:

```bash
# Garantir que estás dentro da pasta lisboa-pedala
cd lisboa-pedala

# Executar a CLI
python -m src.cli
```

### Menu de Opções Disponíveis:

* **Opção 1 (Inicializar BD):** popula a base de dados SQLite (`lisboa_pedala.db`) com utilizadores de teste, estações (Baixa, Saldanha, Campo Grande) e docas com bicicletas, repondo o inventário original;
* **Opção 2 (Demonstrar US-1):** permite simular interativamente uma viagem com duração personalizável em minutos para demonstrar a aplicação das regras tarifárias (45 min gratuitos de passe anual vs blocos excedentes de 0.50€, ou taxa de utilizadores ocasionais);
* **Opção 3 (Demonstrar US-3):** envia um lote com eventos simulados de uma doca que esteve offline, comprovando o descarte de duplicados por idempotência;
* **Opção 4 (Demonstrar US-4):** emite na consola o resumo municipal e o detalhe por freguesia com cálculo de $CO_2$ evitado.
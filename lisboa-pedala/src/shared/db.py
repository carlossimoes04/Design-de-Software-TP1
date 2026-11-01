"""
Gestão Centralizada da Base de Dados Relacional SQLite.
Garante a dissociação estrutural exigida pelo RGPD (ARCHITECTURE.md §3.C).
"""

import sqlite3
from pathlib import Path

DB_FILE = Path(__file__).resolve().parent.parent.parent / "lisboa_pedala.db"


def get_connection(db_path: str = None) -> sqlite3.Connection:
    """Abre ou devolve uma conexão ativa ao SQLite com row_factory ativada."""
    path = db_path or str(DB_FILE)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = None):
    """Cria as tabelas do sistema se ainda não existirem."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.executescript("""
    -- 1. Utilizadores (Assinantes e Ocasionais)
    CREATE TABLE IF NOT EXISTS utilizadores (
        id TEXT PRIMARY KEY,
        nif TEXT NOT NULL UNIQUE,
        nome TEXT NOT NULL,
        email TEXT NOT NULL,
        tem_passe_ativo INTEGER NOT NULL DEFAULT 1,
        tipo_passe TEXT NOT NULL DEFAULT 'ANUAL',
        saldo REAL NOT NULL DEFAULT 0.0
    );

    -- 2. Estações Municipais
    CREATE TABLE IF NOT EXISTS estacoes (
        id TEXT PRIMARY KEY,
        nome TEXT NOT NULL,
        freguesia TEXT NOT NULL,
        capacidade INTEGER NOT NULL
    );

    -- 3. Bicicletas da Frota
    CREATE TABLE IF NOT EXISTS bicicletas (
        id TEXT PRIMARY KEY,
        eletrica INTEGER NOT NULL DEFAULT 1,
        nivel_bateria REAL NOT NULL DEFAULT 100.0,
        avariada INTEGER NOT NULL DEFAULT 0
    );

    -- 4. Docas Físicas
    CREATE TABLE IF NOT EXISTS docas (
        id TEXT PRIMARY KEY,
        estacao_id TEXT NOT NULL,
        bicicleta_id TEXT,
        estado TEXT NOT NULL DEFAULT 'LIVRE',
        FOREIGN KEY (estacao_id) REFERENCES estacoes (id),
        FOREIGN KEY (bicicleta_id) REFERENCES bicicletas (id)
    );

    -- 5. Viagens (Dissociação RGPD: sem colunas com dados pessoais ou GPS direto)
    CREATE TABLE IF NOT EXISTS viagens (
        id TEXT PRIMARY KEY,
        utilizador_id TEXT NOT NULL,
        bicicleta_id TEXT NOT NULL,
        doca_inicio_id TEXT NOT NULL,
        hora_inicio TEXT NOT NULL,
        doca_fim_id TEXT,
        hora_fim TEXT,
        duracao_minutos INTEGER DEFAULT 0,
        custo REAL DEFAULT 0.0,
        hash_idempotencia TEXT UNIQUE,
        estado TEXT NOT NULL DEFAULT 'EM_CURSO',
        FOREIGN KEY (utilizador_id) REFERENCES utilizadores (id),
        FOREIGN KEY (bicicleta_id) REFERENCES bicicletas (id)
    );

    -- 6. Faturas Emitidas (Retenção fiscal de 10 anos)
    CREATE TABLE IF NOT EXISTS faturas (
        id TEXT PRIMARY KEY,
        viagem_id TEXT NOT NULL UNIQUE,
        nif TEXT NOT NULL,
        valor REAL NOT NULL,
        data_emissao TEXT NOT NULL,
        paga INTEGER NOT NULL DEFAULT 1,
        FOREIGN KEY (viagem_id) REFERENCES viagens (id)
    );

    -- 7. Histórico de Eventos Offline Processados (Garantia de Idempotência US-3)
    CREATE TABLE IF NOT EXISTS eventos_offline_processados (
        hash_idempotencia TEXT PRIMARY KEY,
        processado_em TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()


def seed_dados_iniciais(db_path: str = None):
    """Popula a base de dados com dados iniciais para testar as User Stories (US-1 e US-4)."""
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()

    # Utilizadores de Teste
    cursor.execute("""
        INSERT OR IGNORE INTO utilizadores (id, nif, nome, email, tem_passe_ativo, tipo_passe, saldo)
        VALUES 
            ('user_assinante_1', '123456789', 'Maria Silva', 'maria.silva@fcul.pt', 1, 'ANUAL', 30.0),
            ('user_ocasional_1', '987654321', 'Pedro Santos', 'pedro.santos@gmail.com', 0, 'OCASIONAL', 10.0);
    """)

    # Estações por Freguesia
    cursor.execute("""
        INSERT OR IGNORE INTO estacoes (id, nome, freguesia, capacidade)
        VALUES 
            ('est_baixa', 'Baixa-Chiado', 'Santa Maria Maior', 10),
            ('est_saldanha', 'Saldanha / Duque de Ávila', 'Avenidas Novas', 12),
            ('est_campo_grande', 'Campo Grande / FCUL', 'Alvalade', 15);
    """)

    # Bicicletas
    cursor.execute("""
        INSERT OR IGNORE INTO bicicletas (id, eletrica, nivel_bateria, avariada)
        VALUES 
            ('bike_01', 1, 95.0, 0),
            ('bike_02', 1, 80.0, 0),
            ('bike_03', 0, 100.0, 0);
    """)

    # Docas
    cursor.execute("""
        INSERT OR IGNORE INTO docas (id, estacao_id, bicicleta_id, estado)
        VALUES 
            ('doca_baixa_1', 'est_baixa', 'bike_01', 'OCUPADA'),
            ('doca_baixa_2', 'est_baixa', NULL, 'LIVRE'),
            ('doca_saldanha_1', 'est_saldanha', 'bike_02', 'OCUPADA'),
            ('doca_saldanha_2', 'est_saldanha', NULL, 'LIVRE'),
            ('doca_campo_grande_1', 'est_campo_grande', NULL, 'LIVRE'),
            ('doca_campo_grande_2', 'est_campo_grande', NULL, 'LIVRE');
    """)

    conn.commit()
    conn.close()
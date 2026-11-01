"""
Componente ManutencaoFrota (src.manutencao.manutencao_frota).
Responsabilidade: Gestão de ordens de trabalho e reparação de avarias de bicicletas.
Métricas e Estabilidade: Puramente estável (Ce = 0, I = 0.00), conforme docs/02-componentes.md (§4.1).
Conascência: Mitigação de conascência de significado com estacoes (docs/02-componentes.md §5.1).
Contrato Arquitetural: Contrato 3 do .importlinter (proibido importar outros domínios de negócio).
Atribuição: Aluno 2 (CODEOWNERS e docs/03-particionamento-e-vistas.md §4.2).
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from src.shared.db import get_connection
from src.shared.models import EstadoDoca


class ManutencaoFrota:
    """Gere o ciclo de vida das ordens de trabalho dos 25 técnicos de manutenção (Requisito 5)."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        self._init_tabela()

    def _init_tabela(self):
        """Garante a existência da tabela de ordens de manutenção no SQLite."""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ordens_manutencao (
                id TEXT PRIMARY KEY,
                bicicleta_id TEXT NOT NULL,
                motivo TEXT NOT NULL,
                estado TEXT NOT NULL DEFAULT 'PENDENTE',
                data_abertura TEXT NOT NULL,
                tecnico_id TEXT,
                data_conclusao TEXT,
                FOREIGN KEY (bicicleta_id) REFERENCES bicicletas (id)
            );
        """)
        conn.commit()
        conn.close()

    def abrir_ordem_manutencao(self, bicicleta_id: str, motivo: str) -> Dict[str, Any]:
        """
        Abre uma ordem de trabalho de reparação e marca a bicicleta como avariada.
        Conforme a conascência de significado (CoM), alinha o estado com EstadoDoca.AVARIADA.
        """
        ordem_id = f"MAN-{datetime.now().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
        data_abertura = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = get_connection(self.db_path)
        cursor = conn.cursor()

        # Inserir ordem de serviço
        cursor.execute("""
            INSERT INTO ordens_manutencao (id, bicicleta_id, motivo, estado, data_abertura)
            VALUES (?, ?, ?, 'PENDENTE', ?)
        """, (ordem_id, bicicleta_id, motivo, data_abertura))

        # Atualizar bicicleta para estado avariado
        cursor.execute("UPDATE bicicletas SET avariada = 1 WHERE id = ?", (bicicleta_id,))
        conn.commit()
        conn.close()

        return {
            "ordem_id": ordem_id,
            "bicicleta_id": bicicleta_id,
            "motivo": motivo,
            "estado": "PENDENTE",
            "data_abertura": data_abertura,
        }

    def listar_ordens_pendentes(self) -> List[Dict[str, Any]]:
        """Lista todas as ordens de reparação que aguardam intervenção técnica."""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, bicicleta_id, motivo, estado, data_abertura, tecnico_id
            FROM ordens_manutencao WHERE estado = 'PENDENTE'
            ORDER BY data_abertura ASC
        """)
        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "id": r["id"],
                "bicicleta_id": r["bicicleta_id"],
                "motivo": r["motivo"],
                "estado": r["estado"],
                "data_abertura": r["data_abertura"],
                "tecnico_id": r["tecnico_id"],
            }
            for r in rows
        ]

    def concluir_ordem_manutencao(self, ordem_id: str, tecnico_id: str = "tec_01") -> bool:
        """
        Regista a conclusão da reparação por um técnico e repõe a bicicleta como operacional.
        """
        data_conclusao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = get_connection(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT bicicleta_id FROM ordens_manutencao WHERE id = ?", (ordem_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return False

        bicicleta_id = row["bicicleta_id"]

        cursor.execute("""
            UPDATE ordens_manutencao 
            SET estado = 'CONCLUIDA', tecnico_id = ?, data_conclusao = ?
            WHERE id = ?
        """, (tecnico_id, data_conclusao, ordem_id))

        cursor.execute("UPDATE bicicletas SET avariada = 0 WHERE id = ?", (bicicleta_id,))
        conn.commit()
        conn.close()
        return True
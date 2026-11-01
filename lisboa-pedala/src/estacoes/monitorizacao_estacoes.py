"""
Componente MonitorizacaoEstacoes (src.estacoes.monitorizacao_estacoes).
Responsabilidade: Gestão da ocupação e estado mecânico das docas em tempo real.
"""

from typing import Optional, List
from src.shared.db import get_connection
from src.shared.models import EstacaoDTO, DocaDTO, EstadoDoca
from src.shared.simuladores import SimuladorDoca

from src.utilizadores.conta_utilizador import ContaUtilizador


class MonitorizacaoEstacoes:
    """Gere o inventário das estações e a operação mecânica das docas."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        self.conta_utilizador = ContaUtilizador(db_path)

    def obter_estacao(self, estacao_id: str) -> Optional[EstacaoDTO]:
        """Obtém os detalhes de uma estação."""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, freguesia, capacidade FROM estacoes WHERE id = ?", (estacao_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None
        return EstacaoDTO(
            id=row["id"],
            nome=row["nome"],
            freguesia=row["freguesia"],
            capacidade=row["capacidade"]
        )

    def listar_estacoes(self) -> List[EstacaoDTO]:
        """Lista todas as estações disponíveis no município."""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, freguesia, capacidade FROM estacoes")
        rows = cursor.fetchall()
        conn.close()

        return [
            EstacaoDTO(
                id=r["id"],
                nome=r["nome"],
                freguesia=r["freguesia"],
                capacidade=r["capacidade"]
            )
            for r in rows
        ]

    def obter_docas_da_estacao(self, estacao_id: str) -> List[DocaDTO]:
        """Lista todas as docas de uma estação e respetivo estado."""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, estacao_id, bicicleta_id, estado FROM docas WHERE estacao_id = ?",
            (estacao_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        return [
            DocaDTO(
                id=r["id"],
                estacao_id=r["estacao_id"],
                bicicleta_id=r["bicicleta_id"],
                estado=EstadoDoca(r["estado"])
            )
            for r in rows
        ]

    def destrancar_bicicleta_doca(self, doca_id: str, utilizador_id: str) -> tuple[bool, str, Optional[str]]:
        """
        Liberta a bicicleta de uma doca.
        ⚠️ Método gerado com acoplamento indevido a ContaUtilizador.
        """
        # Violação: Estações a verificar regras de contas de utilizadores
        valido, motivo = self.conta_utilizador.validar_elegibilidade_desbloqueio(utilizador_id)
        if not valido:
            return False, f"Desbloqueio recusado: {motivo}", None

        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, bicicleta_id, estado FROM docas WHERE id = ?", (doca_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return False, "Doca inexistente.", None

        if row["estado"] != EstadoDoca.OCUPADA.value or not row["bicicleta_id"]:
            conn.close()
            return False, "Doca não tem bicicleta disponível para desbloqueio.", None

        bicicleta_id = row["bicicleta_id"]

        # Acionar simulador físico da doca
        simulador = SimuladorDoca(doca_id)
        simulador.destrancar(bicicleta_id)

        # Atualizar BD: doca fica LIVRE e sem bicicleta associada
        cursor.execute(
            "UPDATE docas SET bicicleta_id = NULL, estado = ? WHERE id = ?",
            (EstadoDoca.LIVRE.value, doca_id)
        )
        conn.commit()
        conn.close()

        return True, "Bicicleta destrancada com sucesso.", bicicleta_id

    def receber_bicicleta_doca(self, doca_id: str, bicicleta_id: str) -> tuple[bool, str]:
        """Encaixa e tranca uma bicicleta numa doca livre (devolução US-1)."""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, estado FROM docas WHERE id = ?", (doca_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return False, "Doca de destino inexistente."

        if row["estado"] != EstadoDoca.LIVRE.value:
            conn.close()
            return False, "Doca de destino não está livre para receber bicicleta."

        # Acionar simulador físico de encaixe
        simulador = SimuladorDoca(doca_id)
        simulador.trancar(bicicleta_id)

        # Atualizar estado na BD para OCUPADA
        cursor.execute(
            "UPDATE docas SET bicicleta_id = ?, estado = ? WHERE id = ?",
            (bicicleta_id, EstadoDoca.OCUPADA.value, doca_id)
        )
        conn.commit()
        conn.close()

        return True, "Bicicleta encaixada e trancada com sucesso na doca."
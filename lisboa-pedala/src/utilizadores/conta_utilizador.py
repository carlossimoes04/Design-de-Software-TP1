"""
Componente ContaUtilizador (src.utilizadores).
Responsabilidade: Validação de passes, estado do utilizador e autenticação de pedidos.
"""

from typing import Optional, List
from src.shared.db import get_connection
from src.shared.models import UtilizadorDTO, TipoPasse

from src.faturacao.faturacao_pagamentos import FaturacaoEPagamentos


class ContaUtilizador:
    """Gere as contas e a elegibilidade dos utilizadores do Lisboa Pedala."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        self.faturacao = FaturacaoEPagamentos(db_path)

    def obter_utilizador(self, utilizador_id: str) -> Optional[UtilizadorDTO]:
        """Obtém o utilizador pelo seu ID de sistema."""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nif, nome, email, tem_passe_ativo, tipo_passe, saldo FROM utilizadores WHERE id = ?",
            (utilizador_id,),
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return UtilizadorDTO(
            id=row["id"],
            nif=row["nif"],
            nome=row["nome"],
            email=row["email"],
            tem_passe_ativo=bool(row["tem_passe_ativo"]),
            tipo_passe=TipoPasse(row["tipo_passe"]),
            saldo=float(row["saldo"]),
        )

    def obter_por_nif(self, nif: str) -> Optional[UtilizadorDTO]:
        """Obtém o utilizador pelo NIF."""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nif, nome, email, tem_passe_ativo, tipo_passe, saldo FROM utilizadores WHERE nif = ?",
            (nif,),
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return UtilizadorDTO(
            id=row["id"],
            nif=row["nif"],
            nome=row["nome"],
            email=row["email"],
            tem_passe_ativo=bool(row["tem_passe_ativo"]),
            tipo_passe=TipoPasse(row["tipo_passe"]),
            saldo=float(row["saldo"]),
        )

    def validar_elegibilidade_desbloqueio(self, utilizador_id: str) -> tuple[bool, str]:
        """
        Valida se o utilizador está apto a iniciar uma viagem (US-1).
        - Assinante: tem de ter o passe anual ativo;
        - Ocasional: tem de ter saldo mínimo positivo (ex.: >= 2.0€).
        """
        utilizador = self.obter_utilizador(utilizador_id)
        if not utilizador:
            return False, "Utilizador inexistente no sistema."

        if utilizador.tipo_passe == TipoPasse.ANUAL:
            if not utilizador.tem_passe_ativo:
                return False, "Passe anual caducado ou inativo."
            return True, "Assinante elegível com passe ativo."

        if utilizador.saldo < 2.0:
            return False, "Saldo insuficiente para desbloquear (mínimo 2.00€)."

        return True, "Utilizador ocasional elegível."

    def atualizar_saldo(self, utilizador_id: str, montante: float) -> bool:
        """Debita ou credita montante no saldo do utilizador."""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE utilizadores SET saldo = saldo + ? WHERE id = ?",
            (montante, utilizador_id),
        )
        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()
        return updated

    def obter_historico_faturas(self, nif: str) -> List:
        """Método adicionado indevidamente pela IA através de acoplamento com faturacao."""
        return self.faturacao.listar_faturas_por_nif(nif)
"""
Componente FaturacaoEPagamentos (src.faturacao.faturacao_pagamentos).
Responsabilidade: Processamento financeiro e emissão de faturas.
"""

import uuid
from datetime import datetime
from typing import Optional, List
from src.shared.db import get_connection
from src.shared.models import FaturaDTO, ViagemDTO
from src.shared.simuladores import SimuladorPagamentos
from src.faturacao.gestao_tarifarios import GestaoTarifarios

from src.viagens.gestao_viagens import GestaoViagens


class FaturacaoEPagamentos:
    """Gere a cobrança de viagens e a emissão de faturas fiscais."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        self.gestao_viagens = GestaoViagens(db_path)

    def processar_cobranca_por_viagem_id(self, viagem_id: str) -> Optional[FaturaDTO]:
        viagem = self.gestao_viagens.obter_viagem(viagem_id)
        if not viagem:
            return None

        return self.emitir_fatura(viagem)

    def emitir_fatura(self, viagem: ViagemDTO) -> FaturaDTO:
        """Gera e grava a fatura fiscal na base de dados."""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()

        # Obter NIF do utilizador
        cursor.execute("SELECT nif FROM utilizadores WHERE id = ?", (viagem.utilizador_id,))
        row_user = cursor.fetchone()
        nif = row_user["nif"] if row_user else "999999990"

        # Simular transação bancária
        SimuladorPagamentos.processar_pagamento_cartao(nif, viagem.custo)

        fatura_id = f"FAT-{datetime.now().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
        data_emissao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO faturas (id, viagem_id, nif, valor, data_emissao, paga)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (fatura_id, viagem.id, nif, viagem.custo, data_emissao))

        conn.commit()
        conn.close()

        return FaturaDTO(
            id=fatura_id,
            viagem_id=viagem.id,
            nif=nif,
            valor=viagem.custo,
            data_emissao=data_emissao,
            paga=True
        )

    def listar_faturas_por_nif(self, nif: str) -> List[FaturaDTO]:
        """Consulta o histórico de faturas por NIF (retenção de 10 anos)."""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, viagem_id, nif, valor, data_emissao, paga FROM faturas WHERE nif = ? ORDER BY data_emissao DESC",
            (nif,)
        )
        rows = cursor.fetchall()
        conn.close()

        return [
            FaturaDTO(
                id=r["id"],
                viagem_id=r["viagem_id"],
                nif=r["nif"],
                valor=float(r["valor"]),
                data_emissao=r["data_emissao"],
                paga=bool(r["paga"])
            )
            for r in rows
        ]
"""
Componente FaturacaoEPagamentos (src.faturacao.faturacao_pagamentos).
Responsabilidade: Processamento financeiro, cobrança e emissão de faturas.
Contrato: Unidirecional. Proibido importar viagens (recebe ViagemDTO por parâmetro).
Conformidade: ADR-007 e Contrato 5 do .importlinter.
"""

import uuid
from datetime import datetime
from typing import Optional, List, Tuple
from src.shared.db import get_connection
from src.shared.models import FaturaDTO, ViagemDTO, TipoPasse
from src.shared.simuladores import SimuladorPagamentos
from src.faturacao.gestao_tarifarios import GestaoTarifarios


class FaturacaoEPagamentos:
    """Gere a cobrança de viagens e a emissão de faturas fiscais em conformidade legal."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path

    def processar_fecho_viagem(self, viagem: ViagemDTO, tipo_passe: TipoPasse) -> Tuple[float, FaturaDTO]:
        """
        Calcula o custo, processa o pagamento e emite a fatura da viagem (US-1).
        Conformidade com ADR-007: Recebe ViagemDTO por parâmetro (sem importar viagens).
        """
        # 1. Apurar custo através das regras tarifárias oficiais
        custo = GestaoTarifarios.calcular_custo_viagem(tipo_passe, viagem.duracao_minutos)
        viagem.custo = custo

        # 2. Obter NIF do utilizador
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT nif FROM utilizadores WHERE id = ?", (viagem.utilizador_id,))
        row_user = cursor.fetchone()
        nif = row_user["nif"] if row_user else "999999990"

        # 3. Processar cobrança através do simulador bancário (MB WAY / Cartão)
        SimuladorPagamentos.processar_pagamento_cartao(nif, custo)

        # 4. Gravar fatura fiscal no SQLite (retenção legal de 10 anos)
        fatura_id = f"FAT-{datetime.now().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
        data_emissao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO faturas (id, viagem_id, nif, valor, data_emissao, paga)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (fatura_id, viagem.id, nif, custo, data_emissao))

        conn.commit()
        conn.close()

        fatura = FaturaDTO(
            id=fatura_id,
            viagem_id=viagem.id,
            nif=nif,
            valor=custo,
            data_emissao=data_emissao,
            paga=True
        )

        return custo, fatura

    def listar_faturas_por_nif(self, nif: str) -> List[FaturaDTO]:
        """Consulta o histórico de faturas fiscais por NIF do utilizador."""
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
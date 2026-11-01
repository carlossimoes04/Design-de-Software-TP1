"""
Simuladores de Periféricos de Hardware e Serviços Externos.
Isolam a aplicação de IoT físico e de gateways bancárias reais.
"""

import hashlib
from typing import List, Dict, Any
from src.shared.models import EventoDocaOfflineDTO
from src.shared.hash_utils import gerar_hash_viagem


class SimuladorDoca:
    """Simulador mecânico das docas das estações (US-1 e US-3)."""

    def __init__(self, doca_id: str):
        self.doca_id = doca_id
        self.trancada = True
        self.bicicleta_id: str | None = None

    def destrancar(self, bicicleta_id: str) -> bool:
        """Simula o desbloqueio mecânico da tranca física."""
        self.trancada = False
        self.bicicleta_id = None
        return True

    def trancar(self, bicicleta_id: str) -> bool:
        """Simula o fecho do trinco e deteção do sensor da bicicleta."""
        self.trancada = True
        self.bicicleta_id = bicicleta_id
        return True

    @staticmethod
    def gerar_lote_eventos_offline(eventos_raw: List[Dict[str, str]]) -> List[EventoDocaOfflineDTO]:
        """
        Simula a acumulação de eventos em memória local na doca (até 24h sem rede)
        e calcula o identificador determinístico de idempotência para cada viagem.
        """
        lote = []
        for ev in eventos_raw:
            h = gerar_hash_viagem(ev["doca_id"], ev["bicicleta_id"], ev["timestamp_inicio"])
            lote.append(
                EventoDocaOfflineDTO(
                    doca_id=ev["doca_id"],
                    bicicleta_id=ev["bicicleta_id"],
                    timestamp_inicio=ev["timestamp_inicio"],
                    timestamp_fim=ev["timestamp_fim"],
                    hash_idempotencia=h,
                )
            )
        return lote


class SimuladorPagamentos:
    """Simulador de Gateway Financeira (MB WAY e Cartão) (US-1)."""

    @staticmethod
    def processar_pagamento_mbway(telemovel: str, valor: float) -> Dict[str, Any]:
        """Simula autorização e débito imediato via MB WAY."""
        if valor <= 0.0:
            return {"sucesso": True, "transacao_id": "ISENTO", "mensagem": "Sem custos excedentes"}
        tx_id = f"MBW-{hashlib.md5(f'{telemovel}:{valor}'.encode()).hexdigest()[:8].upper()}"
        return {
            "sucesso": True,
            "transacao_id": tx_id,
            "mensagem": "Cobrança autorizada com sucesso via MB WAY",
        }

    @staticmethod
    def processar_pagamento_cartao(nif: str, valor: float) -> Dict[str, Any]:
        """Simula autorização e débito via Cartão de Débito/Crédito."""
        if valor <= 0.0:
            return {"sucesso": True, "transacao_id": "ISENTO", "mensagem": "Sem custos excedentes"}
        tx_id = f"CC-{hashlib.md5(f'{nif}:{valor}'.encode()).hexdigest()[:8].upper()}"
        return {
            "sucesso": True,
            "transacao_id": tx_id,
            "mensagem": "Cobrança autorizada com sucesso via Cartão",
        }
"""
Componente SincronizacaoDocas (src.viagens.sincronizacao_docas).
Responsabilidade: Processamento e desduplicação de registos diferidos de viagens
enviados em lote por docas offline (US-3).
Conformidade: ADR-001 (§3.A), ADR-004 e Contrato 6 do .importlinter.
"""

from typing import List, Dict, Any, Optional
from src.shared.models import EventoDocaOfflineDTO
from src.shared.simuladores import SimuladorDoca
from src.viagens.gestao_viagens import GestaoViagens


class SincronizacaoDocas:
    """Processa lotes de viagens acumuladas por docas sem rede com garantia de idempotência (US-3)."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        self.gestao_viagens = GestaoViagens(db_path)

    def processar_lote_eventos(self, lote: List[EventoDocaOfflineDTO]) -> Dict[str, Any]:
        """
        Recebe um lote de eventos de viagens diferidas de uma doca.
        Submete cada evento ao GestaoViagens, garantindo que reenvios são descartados sem duplicados.
        """
        processados = 0
        duplicados = 0
        falhas = 0
        detalhes = []

        for evento in lote:
            sucesso, msg = self.gestao_viagens.registar_viagem_offline_idempotente(
                doca_inicio_id=evento.doca_id,
                bicicleta_id=evento.bicicleta_id,
                timestamp_inicio=evento.timestamp_inicio,
                timestamp_fim=evento.timestamp_fim,
                hash_idempotencia=evento.hash_idempotencia,
            )

            if sucesso:
                processados += 1
                detalhes.append(f"Sucesso [{evento.hash_idempotencia[:8]}]: {msg}")
            elif "duplicado" in msg.lower():
                duplicados += 1
                detalhes.append(f"Idempotência [{evento.hash_idempotencia[:8]}]: {msg}")
            else:
                falhas += 1
                detalhes.append(f"Falha [{evento.hash_idempotencia[:8]}]: {msg}")

        return {
            "total_recebidos": len(lote),
            "processados_sucesso": processados,
            "duplicados_descartados": duplicados,
            "falhas": falhas,
            "detalhes": detalhes,
        }

    def simular_reenvio_doca_offline(self, doca_id: str, eventos_raw: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Simula o comportamento de uma doca física quando recupera conectividade de rede móvel:
        Calcula os identificadores SHA-256 e transmite os eventos acumulados ao servidor.
        """
        lote = SimuladorDoca.gerar_lote_eventos_offline(eventos_raw)
        return self.processar_lote_eventos(lote)
"""
Fachada Pública do Pacote src.shared.
Reexporta símbolos comuns para permitir importações limpas e centralizadas.
"""

from src.shared.models import (
    UtilizadorDTO,
    EstacaoDTO,
    DocaDTO,
    BicicletaDTO,
    ViagemDTO,
    FaturaDTO,
    EventoDocaOfflineDTO,
    RelatorioFreguesiaDTO,
    TipoPasse,
    EstadoDoca,
)
from src.shared.hash_utils import gerar_hash_viagem
from src.shared.simuladores import SimuladorDoca, SimuladorPagamentos
from src.shared.db import get_connection, init_db, seed_dados_iniciais

__all__ = [
    "UtilizadorDTO",
    "EstacaoDTO",
    "DocaDTO",
    "BicicletaDTO",
    "ViagemDTO",
    "FaturaDTO",
    "EventoDocaOfflineDTO",
    "RelatorioFreguesiaDTO",
    "TipoPasse",
    "EstadoDoca",
    "gerar_hash_viagem",
    "SimuladorDoca",
    "SimuladorPagamentos",
    "get_connection",
    "init_db",
    "seed_dados_iniciais",
]
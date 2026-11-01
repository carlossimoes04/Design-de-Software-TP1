"""
Modelos de Dados e DTOs Partilhados (Data Transfer Objects).
Camada de Suporte Base: Proibido importar qualquer pacote de domínio.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class TipoPasse(str, Enum):
    ANUAL = "ANUAL"
    OCASIONAL = "OCASIONAL"


class EstadoDoca(str, Enum):
    LIVRE = "LIVRE"
    OCUPADA = "OCUPADA"
    AVARIADA = "AVARIADA"
    EM_MANUTENCAO = "EM_MANUTENCAO"


@dataclass
class UtilizadorDTO:
    id: str
    nif: str
    nome: str
    email: str
    tem_passe_ativo: bool
    tipo_passe: TipoPasse = TipoPasse.ANUAL
    saldo: float = 0.0


@dataclass
class EstacaoDTO:
    id: str
    nome: str
    freguesia: str
    capacidade: int


@dataclass
class DocaDTO:
    id: str
    estacao_id: str
    bicicleta_id: Optional[str] = None
    estado: EstadoDoca = EstadoDoca.LIVRE


@dataclass
class BicicletaDTO:
    id: str
    eletrica: bool
    nivel_bateria: float = 100.0
    avariada: bool = False


@dataclass
class ViagemDTO:
    id: str
    utilizador_id: str
    bicicleta_id: str
    doca_inicio_id: str
    hora_inicio: str
    doca_fim_id: Optional[str] = None
    hora_fim: Optional[str] = None
    duracao_minutos: int = 0
    custo: float = 0.0
    hash_idempotencia: Optional[str] = None
    estado: str = "EM_CURSO"  # "EM_CURSO" ou "CONCLUIDA"


@dataclass
class FaturaDTO:
    id: str
    viagem_id: str
    nif: str
    valor: float
    data_emissao: str
    paga: bool = True


@dataclass
class EventoDocaOfflineDTO:
    doca_id: str
    bicicleta_id: str
    timestamp_inicio: str
    timestamp_fim: str
    hash_idempotencia: str


@dataclass
class RelatorioFreguesiaDTO:
    freguesia: str
    total_viagens: int
    duracao_total_minutos: int
    co2_evitado_kg: float
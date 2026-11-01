"""
Utilitários Criptográficos e Funções de Hashing.
Garante o requisito de Disponibilidade e Idempotência (US-3 / ARCHITECTURE.md §3.A).
"""

import hashlib


def gerar_hash_viagem(doca_id: str, bicicleta_id: str, timestamp_inicio: str) -> str:
    """
    Calcula o hash determinístico SHA-256 para eventos de viagens originados em docas.
    Fórmula: SHA-256(f"{doca_id}:{bicicleta_id}:{timestamp_inicio}")
    Impede a duplicação de registos e cobranças no processamento de lotes offline.
    """
    payload = f"{doca_id}:{bicicleta_id}:{timestamp_inicio}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
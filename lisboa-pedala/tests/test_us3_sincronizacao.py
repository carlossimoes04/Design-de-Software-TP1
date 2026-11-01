import pytest
from src.shared.db import get_connection, init_db, seed_dados_iniciais
from src.viagens.sincronizacao_docas import SincronizacaoDocas


@pytest.fixture(autouse=True)
def setup_database():
    """Garante uma base de dados limpa e populada antes de cada teste."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM faturas;")
    cursor.execute("DELETE FROM viagens;")
    cursor.execute("DELETE FROM eventos_offline_processados;")
    conn.commit()
    conn.close()
    seed_dados_iniciais()


def test_sincronizacao_offline_idempotencia():
    """Valida o reenvio de lote offline e a rejeição de eventos duplicados por SHA-256."""
    sinc = SincronizacaoDocas()
    doca_id = "doca_campo_grande_1"

    eventos_raw = [
        {
            "doca_id": doca_id,
            "bicicleta_id": "bike_03",
            "timestamp_inicio": "2026-06-01T10:00:00",
            "timestamp_fim": "2026-06-01T10:25:00"
        },
        {
            "doca_id": doca_id,
            "bicicleta_id": "bike_03",
            "timestamp_inicio": "2026-06-01T10:00:00",
            "timestamp_fim": "2026-06-01T10:25:00"  # Duplicado exato
        }
    ]

    resultado = sinc.simular_reenvio_doca_offline(doca_id, eventos_raw)

    assert resultado["total_recebidos"] == 2
    assert resultado["processados_sucesso"] == 1
    assert resultado["duplicados_descartados"] == 1
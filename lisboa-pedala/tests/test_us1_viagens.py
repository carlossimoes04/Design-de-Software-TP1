import pytest
from src.shared.db import get_connection, init_db, seed_dados_iniciais
from src.viagens.gestao_viagens import GestaoViagens


@pytest.fixture(autouse=True)
def setup_database():
    """Garante uma base de dados limpa e populada antes de cada teste."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    # Limpar tabelas de estado para garantir idempotência nos testes
    cursor.execute("DELETE FROM faturas;")
    cursor.execute("DELETE FROM viagens;")
    cursor.execute("DELETE FROM eventos_offline_processados;")
    cursor.execute("UPDATE docas SET bicicleta_id = 'bike_01', estado = 'OCUPADA' WHERE id = 'doca_baixa_1';")
    cursor.execute("UPDATE docas SET bicicleta_id = NULL, estado = 'LIVRE' WHERE id = 'doca_saldanha_2';")
    conn.commit()
    conn.close()
    seed_dados_iniciais()


def test_viagem_completa_sucesso():
    """Valida o ciclo completo: desbloqueio, percurso, fecho de viagem e faturação."""
    gestao = GestaoViagens()
    utilizador_id = "user_assinante_1"
    doca_origem = "doca_baixa_1"
    doca_destino = "doca_saldanha_2"

    # 1. Iniciar viagem
    sucesso, msg, viagem = gestao.iniciar_viagem(utilizador_id, doca_origem)
    assert sucesso is True, f"Falha ao iniciar viagem: {msg}"
    assert viagem is not None
    assert viagem.estado == "EM_CURSO"

    # 2. Terminar viagem e cobrar
    sucesso_ter, msg_ter, resultado = gestao.terminar_viagem(viagem.id, doca_destino)
    assert sucesso_ter is True, f"Falha ao terminar viagem: {msg_ter}"
    assert resultado is not None

    v_obj, fatura_obj = resultado
    assert v_obj.estado == "CONCLUIDA"
    assert v_obj.doca_fim_id == doca_destino
    assert fatura_obj is not None
    assert fatura_obj.nif == "123456789"
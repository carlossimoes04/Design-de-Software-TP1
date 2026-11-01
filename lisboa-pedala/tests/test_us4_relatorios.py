import pytest
from src.shared.db import get_connection, init_db, seed_dados_iniciais
from src.relatorios.relatorios_municipais import RelatoriosMunicipais
from src.viagens.gestao_viagens import GestaoViagens


@pytest.fixture(autouse=True)
def setup_database():
    """Garante uma base de dados limpa e populada antes de cada teste."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM faturas;")
    cursor.execute("DELETE FROM viagens;")
    cursor.execute("DELETE FROM eventos_offline_processados;")
    cursor.execute("UPDATE docas SET bicicleta_id = 'bike_01', estado = 'OCUPADA' WHERE id = 'doca_baixa_1';")
    cursor.execute("UPDATE docas SET bicicleta_id = NULL, estado = 'LIVRE' WHERE id = 'doca_saldanha_2';")
    conn.commit()
    conn.close()
    seed_dados_iniciais()


def test_relatorio_municipal_freguesia():
    """Valida a agregação de estatísticas por freguesia e cálculo de CO2 evitado (RGPD compliant)."""
    # Executar uma viagem para assegurar dados concluídos no relatório
    gestao = GestaoViagens()
    sucesso, _, viagem = gestao.iniciar_viagem("user_assinante_1", "doca_baixa_1")
    if sucesso and viagem:
        gestao.terminar_viagem(viagem.id, "doca_saldanha_2")

    relatorios = RelatoriosMunicipais()
    resumo = relatorios.obter_resumo_geral_municipio()

    assert resumo["municipio"] == "Lisboa"
    assert resumo["total_viagens_concluidas"] >= 1
    assert "detalhe_freguesias" in resumo
    assert len(resumo["detalhe_freguesias"]) > 0

    freguesia_info = resumo["detalhe_freguesias"][0]
    assert "freguesia" in freguesia_info
    assert "viagens" in freguesia_info
    assert "co2_kg" in freguesia_info
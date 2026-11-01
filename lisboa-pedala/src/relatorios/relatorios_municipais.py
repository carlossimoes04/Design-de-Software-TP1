"""
Componente RelatoriosMunicipais (src.relatorios.relatorios_municipais).
Responsabilidade: Consolidação estatística anónima de utilização por freguesia e CO2 evitado (US-4).
Conformidade: ADR-001 (§3.C - RGPD), ADR-007 e Contrato 7 do .importlinter.
"""

from typing import List, Dict, Any, Optional
from src.shared.db import get_connection
from src.shared.models import RelatorioFreguesiaDTO
from src.viagens.gestao_viagens import GestaoViagens


class RelatoriosMunicipais:
    """Compila relatórios de utilização urbana e impacto ecológico para a Câmara de Lisboa."""

    # Fator de emissão evitada: ~0.04 kg de CO2 por minuto pedalado (substituição de tráfego urbano)
    FATOR_CO2_POR_MINUTO = 0.04

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        self.gestao_viagens = GestaoViagens(db_path)

    def obter_relatorio_por_freguesia(self) -> List[RelatorioFreguesiaDTO]:
        """
        Gera o relatório analítico agregado por freguesia (US-4).
        Conformidade com o RGPD: Todos os dados são consolidados sem identificar utilizadores.
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()

        # Agregação relacional por freguesia via doca de início
        cursor.execute("""
            SELECT 
                e.freguesia AS freguesia,
                COUNT(v.id) AS total_viagens,
                COALESCE(SUM(v.duracao_minutos), 0) AS duracao_total_minutos
            FROM viagens v
            JOIN docas d ON v.doca_inicio_id = d.id
            JOIN estacoes e ON d.estacao_id = e.id
            WHERE v.estado = 'CONCLUIDA'
            GROUP BY e.freguesia
            ORDER BY total_viagens DESC
        """)
        rows = cursor.fetchall()
        conn.close()

        relatorios = []
        for r in rows:
            duracao = int(r["duracao_total_minutos"])
            co2 = round(duracao * self.FATOR_CO2_POR_MINUTO, 2)
            relatorios.append(
                RelatorioFreguesiaDTO(
                    freguesia=r["freguesia"],
                    total_viagens=int(r["total_viagens"]),
                    duracao_total_minutos=duracao,
                    co2_evitado_kg=co2
                )
            )

        return relatorios

    def obter_resumo_geral_municipio(self) -> Dict[str, Any]:
        """Apresenta o resumo executivo dos indicadores de sustentabilidade para o executivo camarário."""
        relatorios_freguesia = self.obter_relatorio_por_freguesia()

        total_viagens = sum(r.total_viagens for r in relatorios_freguesia)
        duracao_total = sum(r.duracao_total_minutos for r in relatorios_freguesia)
        co2_total = round(sum(r.co2_evitado_kg for r in relatorios_freguesia), 2)

        return {
            "municipio": "Lisboa",
            "total_viagens_concluidas": total_viagens,
            "tempo_total_minutos": duracao_total,
            "tempo_total_horas": round(duracao_total / 60.0, 1),
            "co2_total_evitado_kg": co2_total,
            "freguesias_ativas": len(relatorios_freguesia),
            "detalhe_freguesias": [
                {
                    "freguesia": r.freguesia,
                    "viagens": r.total_viagens,
                    "minutos": r.duracao_total_minutos,
                    "co2_kg": r.co2_evitado_kg
                }
                for r in relatorios_freguesia
            ]
        }
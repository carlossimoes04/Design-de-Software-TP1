"""
Componente RedistribuicaoFrota (src.estacoes.redistribuicao_frota).
Responsabilidade: Análise de equilíbrio e sugestão de rotas para as 6 carrinhas municipais.
Localização Arquitetural: Submódulo de src.estacoes, conforme Decisão 4 do ADR-007.
Métricas e Estabilidade: Ce = 1 (acopla internamente a MonitorizacaoEstacoes), I = 1.00 (docs/02-componentes.md §4.1).
Contrato Arquitetural: Contrato 4 do .importlinter (proibido acoplar a viagens, faturacao ou utilizadores).
Atribuição: Aluno 2 (CODEOWNERS e docs/03-particionamento-e-vistas.md §4.2).
"""

from typing import Optional, List, Dict, Any
from src.shared.models import EstadoDoca
from src.estacoes.monitorizacao_estacoes import MonitorizacaoEstacoes


class RedistribuicaoFrota:
    """Calcula alertas de ocupação e rotas de reequilíbrio para as carrinhas municipais (Requisito 6)."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        self.monitorizacao_estacoes = MonitorizacaoEstacoes(db_path)

    def analisar_necessidades_redistribuicao(self) -> Dict[str, Any]:
        """
        Inspeciona a ocupação de todas as estações e categoriza os desequilíbrios:
        - Ocupação <= 20%: Crítica Vazia (necessita de abastecimento urgente de bicicletas);
        - Ocupação >= 80%: Crítica Cheia (risco iminente de bloqueio de devoluções).
        """
        estacoes = self.monitorizacao_estacoes.listar_estacoes()
        alertas_abastecer = []
        alertas_recolher = []
        resumo_estacoes = []

        for est in estacoes:
            docas = self.monitorizacao_estacoes.obter_docas_da_estacao(est.id)
            total_docas = len(docas)
            if total_docas == 0:
                continue

            ocupadas = sum(1 for d in docas if d.estado == EstadoDoca.OCUPADA)
            taxa_ocupacao = round((ocupadas / total_docas) * 100.0, 1)

            info = {
                "estacao_id": est.id,
                "nome": est.nome,
                "freguesia": est.freguesia,
                "docas_totais": total_docas,
                "bicicletas_disponiveis": ocupadas,
                "taxa_ocupacao_pct": taxa_ocupacao,
            }
            resumo_estacoes.append(info)

            if taxa_ocupacao <= 20.0:
                alertas_abastecer.append({**info, "acao_sugerida": "Abastecer bicicletas"})
            elif taxa_ocupacao >= 80.0:
                alertas_recolher.append({**info, "acao_sugerida": "Recolher bicicletas excedentárias"})

        return {
            "total_estacoes_monitorizadas": len(resumo_estacoes),
            "estacoes_criticas_vazias": len(alertas_abastecer),
            "estacoes_criticas_cheias": len(alertas_recolher),
            "rotas_abastecimento": alertas_abastecer,
            "rotas_recolha": alertas_recolher,
        }

    def sugerir_rotas_carrinhas(self) -> List[Dict[str, Any]]:
        """
        Gera pares de emparelhamento logístico entre estações cheias e vazias
        para orientar as 6 equipas de redistribuição de Lisboa.
        """
        analise = self.analisar_necessidades_redistribuicao()
        cheias = analise["rotas_recolha"]
        vazias = analise["rotas_abastecimento"]

        rotas = []
        for i, (origem, destino) in enumerate(zip(cheias, vazias), start=1):
            rotas.append({
                "rota_id": f"ROTA-{i:02d}",
                "carrinha_designada": f"carrinha_{((i - 1) % 6) + 1:02d}",
                "estacao_recolha": origem["nome"],
                "freguesia_recolha": origem["freguesia"],
                "estacao_entrega": destino["nome"],
                "freguesia_entrega": destino["freguesia"],
                "quantidade_recomendada": 4,
            })

        return rotas
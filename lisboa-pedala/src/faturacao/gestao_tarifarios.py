"""
Componente GestaoTarifarios (src.faturacao.gestao_tarifarios).
Responsabilidade: Aplicação de regras de tarifários e apuramento de custos excedentes.
Contrato: Interno ao módulo faturacao; importa apenas src.shared.
"""

import math
from src.shared.models import TipoPasse


class GestaoTarifarios:
    """Aplica as regras tarifárias oficiais do Lisboa Pedala (US-1)."""

    TARIFA_EXCEDENTE_BLOCO_15MIN = 0.50  # 0.50€ por bloco de 15 min após período gratuito
    TARIFA_BASE_OCASIONAL = 1.50         # Taxa fixa de desbloqueio para ocasionais
    TARIFA_MINUTO_OCASIONAL = 0.15       # 0.15€ por minuto de utilização

    @classmethod
    def calcular_custo_viagem(cls, tipo_passe: TipoPasse, duracao_minutos: int) -> float:
        """
        Calcula o custo final da viagem em euros:
        - Assinante (Passe Anual): Primeiros 45 min são gratuitos.
          Excedentes faturados a 0.50€ por cada fração de 15 min.
        - Ocasional: 1.50€ de taxa de desbloqueio + 0.15€ por minuto.
        """
        if duracao_minutos < 0:
            duracao_minutos = 0

        if tipo_passe == TipoPasse.ANUAL:
            if duracao_minutos <= 45:
                return 0.00
            minutos_excedentes = duracao_minutos - 45
            blocos_15min = math.ceil(minutos_excedentes / 15.0)
            return round(blocos_15min * cls.TARIFA_EXCEDENTE_BLOCO_15MIN, 2)
        else:
            return round(cls.TARIFA_BASE_OCASIONAL + (duracao_minutos * cls.TARIFA_MINUTO_OCASIONAL), 2)
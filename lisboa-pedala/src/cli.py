import sys
import os

# Garantir que a raiz do projeto está no sys.path para importações limpas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.shared.db import init_db, seed_dados_iniciais
from src.viagens.gestao_viagens import GestaoViagens
from src.viagens.sincronizacao_docas import SincronizacaoDocas
from src.relatorios.relatorios_municipais import RelatoriosMunicipais


def menu_principal():
    # Instanciação dos serviços de domínio
    gestao_viagens = GestaoViagens()
    sincronizacao_docas = SincronizacaoDocas()
    relatorios_municipais = RelatoriosMunicipais()

    while True:
        print("\n" + "=" * 60)
        print(" 🚲 LISBOA PEDALA - INTERFACE DE LINHA DE COMANDOS (TP1)")
        print("=" * 60)
        print("1. Inicializar / Carregar dados de teste na Base de Dados")
        print("2. Demonstrar US-1: Viagem Completa (Desbloqueio e Cobrança)")
        print("3. Demonstrar US-3: Sincronização Doca Offline (Idempotência)")
        print("4. Demonstrar US-4: Relatório Municipal por Freguesia")
        print("0. Sair")
        print("=" * 60)

        opcao = input("Escolhe uma opção: ").strip()

        if opcao == "1":
            print("\n[+] A inicializar e popular base de dados de teste...")
            try:
                seed_dados_iniciais()
                print("[✔] Base de dados inicializada com sucesso (utilizadores, estações e docas criadas)!")
            except Exception as e:
                print(f"[✘] Erro ao inicializar base de dados: {e}")

        elif opcao == "2":
            print("\n[--- DEMONSTRAÇÃO US-1: VIAGEM COMPLETA ---]")
            try:
                utilizador_id = "user_assinante_1"
                doca_origem = "doca_baixa_1"
                doca_destino = "doca_saldanha_2"

                print(f"-> A tentar iniciar viagem para '{utilizador_id}' a partir da doca '{doca_origem}'...")
                sucesso, msg, viagem = gestao_viagens.iniciar_viagem(utilizador_id, doca_origem)
                
                if not sucesso or not viagem:
                    print(f"   [✘] Falha ao iniciar viagem: {msg}")
                else:
                    print(f"   [✔] Viagem iniciada com sucesso! (ID: {viagem.id}, Bicicleta: {viagem.bicicleta_id})")

                    print(f"-> A simular percurso e devolução na doca '{doca_destino}'...")
                    sucesso_ter, msg_ter, resultado = gestao_viagens.terminar_viagem(viagem.id, doca_destino)
                    
                    if not sucesso_ter:
                        print(f"   [✘] Falha ao terminar viagem: {msg_ter}")
                    else:
                        print(f"   [✔] {msg_ter}")
                        if resultado:
                            v_obj, fatura_obj = resultado
                            print(f"   [Fatura] Valor cobrado: {v_obj.custo}€ | NIF: {fatura_obj.nif if fatura_obj else 'N/A'}")
            except Exception as e:
                print(f"   [✘] Erro na execução da US-1: {e}")

        elif opcao == "3":
            print("\n[--- DEMONSTRAÇÃO US-3: SINCRONIZAÇÃO OFFLINE E IDEMPOTÊNCIA ---]")
            try:
                doca_id = "doca_campo_grande_1"
                # Eventos offline crus simulados com doca_id incluído
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
                        "timestamp_fim": "2026-06-01T10:25:00"  # Duplicado exato para testar idempotência
                    }
                ]
                print(f"-> A simular reenvio de lote offline pela doca '{doca_id}' com {len(eventos_raw)} eventos...")
                resultado_sinc = sincronizacao_docas.simular_reenvio_doca_offline(doca_id, eventos_raw)
                
                print(f"   [✔] Total recebidos: {resultado_sinc.get('total_recebidos', 0)}")
                print(f"   [✔] Processados com sucesso: {resultado_sinc.get('processados_sucesso', 0)}")
                print(f"   [✔] Duplicados descartados (Idempotência SHA-256): {resultado_sinc.get('duplicados_descartados', 0)}")
                for detalhe in resultado_sinc.get('detalhes', []):
                    print(f"       - {detalhe}")
            except Exception as e:
                print(f"   [✘] Erro na execução da US-3: {e}")

        elif opcao == "4":
            print("\n[--- DEMONSTRAÇÃO US-4: RELATÓRIO MUNICIPAL DE UTILIZAÇÃO ---]")
            try:
                resumo = relatorios_municipais.obter_resumo_geral_municipio()
                print("   [✔] Resumo Executivo Municipal gerado com sucesso (Anónimo / RGPD Compliant):\n")
                print(f"   - Município: {resumo.get('municipio')}")
                print(f"   - Total de Viagens Concluídas: {resumo.get('total_viagens_concluidas')}")
                print(f"   - Tempo Total de Utilização: {resumo.get('tempo_total_minutos')} min ({resumo.get('tempo_total_horas')} h)")
                print(f"   - CO2 Total Evitado: {resumo.get('co2_total_evitado_kg')} kg")
                print("   - Detalhe por Freguesia:")
                for f_detalhe in resumo.get('detalhe_freguesias', []):
                    print(f"     * {f_detalhe['freguesia']:<20} | Viagens: {f_detalhe['viagens']:<3} | Minutos: {f_detalhe['minutos']:<4} | CO2: {f_detalhe['co2_kg']} kg")
            except Exception as e:
                print(f"   [✘] Erro na execução da US-4: {e}")

        elif opcao == "0":
            print("\nA encerrar o Lisboa Pedala. Bom trabalho no TP1!")
            break
        else:
            print("\n[!] Opção inválida. Por favor introduz um número entre 0 e 4.")


if __name__ == "__main__":
    init_db()
    menu_principal()
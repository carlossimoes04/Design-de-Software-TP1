import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime, timedelta
from src.shared.db import get_connection, init_db, seed_dados_iniciais
from src.viagens.gestao_viagens import GestaoViagens
from src.viagens.sincronizacao_docas import SincronizacaoDocas
from src.relatorios.relatorios_municipais import RelatoriosMunicipais


def menu_principal():
    gestao_viagens = GestaoViagens()
    sincronizacao_docas = SincronizacaoDocas()
    relatorios_municipais = RelatoriosMunicipais()

    doca_origem = "doca_baixa_1"
    doca_destino = "doca_saldanha_2"

    while True:
        print("\n" + "=" * 60)
        print(" Lisboa Pedala - Viagens, Sincronização e Relatórios Municipais")
        print("=" * 60)
        print("1. Inicializar / Carregar dados de teste na Base de Dados")
        print("2. Demonstrar US-1: Viagem Completa (Desbloqueio e Cobrança)")
        print("3. Demonstrar US-3: Sincronização Doca Offline (Idempotência)")
        print("4. Demonstrar US-4: Relatório Municipal por Freguesia")
        print("0. Sair")
        print("=" * 60)

        opcao = input("Escolhe uma opção: ").strip()

        if opcao == "1":
            inicializar_db()

        elif opcao == "2":
            try:
                teste_us1(doca_origem, doca_destino, gestao_viagens)
            except Exception as e:
                print(f"   [x] Erro na execução da US-1: {e}")

        elif opcao == "3":
            try:
                teste_u3(sincronizacao_docas)
            except Exception as e:
                print(f"   [x] Erro na execução da US-3: {e}")

        elif opcao == "4":
            try:
                teste_u4(relatorios_municipais)
            except Exception as e:
                print(f"   [x] Erro na execução da US-4: {e}")

        elif opcao == "0":
            print("\nA encerrar o Lisboa Pedala.")
            break
        else:
            print("\n[!] Opção inválida. Por favor introduz um número entre 0 e 4.")

def inicializar_db():
    print("\n[+] A inicializar e popular base de dados de teste...")
    try:
        seed_dados_iniciais()
        print("[✓] Base de dados inicializada com sucesso (utilizadores, estações e docas criadas)!")
    except Exception as e:
        print(f"[x] Erro ao inicializar base de dados: {e}")

def teste_us1(doca_origem: str, doca_destino: str, gestao_viagens: GestaoViagens):
    print("\n[--- Demonstração US-1: Viagem Completa ---]")
    try:
        print("\nEscolhe o perfil para a demonstração:")
        print("1. Assinante (Maria Silva - Passe Anual) [Padrão US-1]")
        print("2. Ocasional (Pedro Santos - Pagamento por Viagem)")

        escolha_u = input("Perfil [Enter para 1]: ").strip()
        utilizador_id = "user_ocasional_1" if escolha_u == "2" else "user_assinante_1"

        print(f"-> A tentar iniciar viagem para '{utilizador_id}' a partir da doca '{doca_origem}'...")
        sucesso, msg, viagem = gestao_viagens.iniciar_viagem(utilizador_id, doca_origem)
        
        if not sucesso or not viagem:
            print(f"   [x] Falha ao iniciar viagem: {msg}")
            print("   [Sugestão] Escolhe a Opção 1 para repor as bicicletas nas docas originais.")
        else:
            print(f"   [✓] Viagem iniciada com sucesso! (ID: {viagem.id}, Bicicleta: {viagem.bicicleta_id})")

            entrada = input("\nQuantos minutos quer simular para esta viagem? [Enter para 60 min]: ").strip()
            minutos_simulados = int(entrada) if entrada.isdigit() else 60
            print(f"-> A simular percurso de {minutos_simulados} minutos até à doca '{doca_destino}'...")

            if minutos_simulados > 0:
                conn = get_connection()
                hora_passada = (datetime.now() - timedelta(minutes=minutos_simulados)).strftime("%Y-%m-%d %H:%M:%S")
                conn.execute("UPDATE viagens SET hora_inicio = ? WHERE id = ?", (hora_passada, viagem.id))
                conn.commit()
                conn.close()
            
            sucesso_ter, msg_ter, resultado = gestao_viagens.terminar_viagem(viagem.id, doca_destino)
            
            if not sucesso_ter:
                print(f"   [x] Falha ao terminar viagem: {msg_ter}")
            else:
                print(f"   [✓] {msg_ter}")
                if resultado:
                    v_obj, fatura_obj = resultado
                    
                    # Obter dados reais do utilizador a partir da BD / modelo de domínio
                    utilizador = gestao_viagens.conta_utilizador.obter_utilizador(utilizador_id)
                    tipo_passe = utilizador.tipo_passe.value if utilizador else "DESCONHECIDO"
                    nome_utilizador = utilizador.nome if utilizador else utilizador_id

                    print(f"\n   --- Resumo do Encerramento e Faturação ---")
                    print(f"   • Utilizador: {nome_utilizador} (NIF: {fatura_obj.nif if fatura_obj else 'N/A'})")
                    print(f"   • Tipo de Passe: {tipo_passe}")
                    print(f"   • Duração Total: {v_obj.duracao_minutos} minutos")

                    # Explicação dinâmica baseada no tipo de passe real
                    if tipo_passe == "ANUAL":
                        print(f"   • Benefício Passe Anual: Primeiros 45 min gratuitos")
                        if v_obj.duracao_minutos > 45:
                            excedente = v_obj.duracao_minutos - 45
                            blocos = (excedente + 14) // 15
                            print(f"   • Excedente: {excedente} min ({blocos} bloco(s) de 15 min a 0.50€)")
                        else:
                            print(f"   • Excedente: 0 min (100% coberto pelo passe)")
                    else:
                        print(f"   • Taxa Base de Desbloqueio: 1.50€")
                        custo_minutos = round(v_obj.duracao_minutos * 0.15, 2)
                        print(f"   • Tempo de Utilização: {v_obj.duracao_minutos} min x 0.15€/min = {custo_minutos}€")

                    print(f"   • Valor Final Cobrado: {v_obj.custo}€")
    except Exception as e:
        print(f"   [x] Erro na execução da US-1: {e}")

def teste_u3(sincronizacao_docas: SincronizacaoDocas):
    print("\n[--- Demonstração US-3: Sincronização Offline e Idempotência ---]")
    try:
        doca_id = "doca_campo_grande_1"

        eventos = [
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
                "timestamp_fim": "2026-06-01T10:25:00"  # duplicado para testar idempotência
            }
        ]

        print(f"-> A simular reenvio de lote offline pela doca '{doca_id}' com {len(eventos)} eventos...")
        resultado_sinc = sincronizacao_docas.simular_reenvio_doca_offline(doca_id, eventos)
        
        print(f"   [✓] Total recebidos: {resultado_sinc.get('total_recebidos', 0)}")
        print(f"   [✓] Processados com sucesso: {resultado_sinc.get('processados_sucesso', 0)}")
        print(f"   [✓] Duplicados descartados (Idempotência SHA-256): {resultado_sinc.get('duplicados_descartados', 0)}")
        for detalhe in resultado_sinc.get('detalhes', []):
            print(f"       - {detalhe}")
    except Exception as e:
        print(f"   [x] Erro na execução da US-3: {e}")

def teste_u4(relatorios_municipais: RelatoriosMunicipais):
    print("\n[--- Demonstração US-4: Relatório Municipal de Utilização ---]")
    try:
        resumo = relatorios_municipais.obter_resumo_geral_municipio()
        print("   [✓] Resumo Executivo Municipal gerado com sucesso (Anónimo / RGPD Compliant):\n")
        print(f"   - Município: {resumo.get('municipio')}")
        print(f"   - Total de Viagens Concluídas: {resumo.get('total_viagens_concluidas')}")
        print(f"   - Tempo Total de Utilização: {resumo.get('tempo_total_minutos')} min ({resumo.get('tempo_total_horas')} h)")
        print(f"   - CO2 Total Evitado: {resumo.get('co2_total_evitado_kg')} kg")
        print("   - Detalhe por Freguesia:")
        for f_detalhe in resumo.get('detalhe_freguesias', []):
            print(f"     * {f_detalhe['freguesia']:<20} | Viagens: {f_detalhe['viagens']:<3} | Minutos: {f_detalhe['minutos']:<4} | CO2: {f_detalhe['co2_kg']} kg")
    except Exception as e:
        print(f"   [x] Erro na execução da US-4: {e}")


if __name__ == "__main__":
    init_db()
    menu_principal()
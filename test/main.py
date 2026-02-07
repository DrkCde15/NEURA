import os
from neura_ai.core import Neura
from neura_ai.config import NeuraConfig

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    # Pergunta o modo de conexão
    print("--- SELEÇÃO DE CONEXÃO ---")
    print("1. Local (127.0.0.1:11434)")
    print("2. Remoto (neura-ai.loca.lt)")
    escolha = input("\nEscolha o modo [1/2]: ").strip()

    host = NeuraConfig.OLLAMA_BASE_URL
    if escolha == "2":
        host = NeuraConfig.TUNNEL_URL
        print(f"📡 Conectando ao túnel: {host}")
    else:
        print(f"🏠 Conectando localmente: {host}")

    # Persona de Veterinária
    system_prompt = (
        "Você é uma veterinária brasileira. Use frases curtas, palavras simples e seja muito realista. "
        "Se receber uma descrição de imagem, interprete como médica. Se não souber, diga que não sabe."
    )

    # Inicializa a Neura
    n = Neura(host=host, system_prompt=system_prompt)

    # Verificação de Saúde
    print("Verificando conexão com o servidor...")
    if not n.health_check():
        print(f"\nERRO: Não foi possível conectar ao servidor em {host}")
        print("Certifique-se de que o Ollama (e o Túnel, se remoto) estão rodando.")
        return

    n.clear_memory()
    clear_screen()

    print("\n--- CONSULTÓRIO VIRTUAL DA NEURA AI ---")
    print(f"Conectado em: {host}")
    print("Comandos: 'analise_imagem', 'limpar memória', 'listar modelos', 'sair'")
    print("Dica: Você pode arrastar uma foto para o terminal para analisá-la.\n")

    while True:
        try:
            entrada = input("👤 Você: ").strip()
            
            # Limpeza de aspas (essencial para Windows)
            entrada = entrada.replace('"', '').replace("'", "")

            if not entrada:
                continue

            if entrada.lower() in ["sair", "parar", "exit", "quit"]: 
                print("👋 Até logo!")
                break
                
            if entrada.lower() in ["limpar memória", "clear"]:
                n.clear_memory()
                print("✨ Memória limpa!")
                continue

            if entrada.lower() in ["listar modelos", "list models", "models"]:
                modelos = n.list_models()
                print(f"🧠 Modelos disponíveis: {', '.join(modelos)}")
                continue

            # Lógica de detecção de imagem
            caminho_foto = None
            if entrada.lower() == "analise_imagem":
                caminho_foto = input("Cole o caminho da imagem: ").strip().replace('"', '').replace("'", "")
            elif entrada.lower().endswith(('.jpg', '.jpeg', '.png')) and os.path.exists(entrada):
                caminho_foto = entrada

            # --- EXECUÇÃO ---
            if caminho_foto:
                print(f"Analisando imagem... (Isso pode levar alguns segundos)")
                # Pede a análise visual
                descricao_ingles = n.get_response("Describe this image objectively", image_path=caminho_foto)
                # Passa a análise para a persona
                resposta_final = n.get_response(f"Abaixo está a descrição técnica de um caso. Comente como veterinária: {descricao_ingles}")
            else:
                # Chat de texto normal
                resposta_final = n.get_response(entrada)

            # Exibe a resposta final
            print(f"\n🤖 Neura: {resposta_final}\n")

        except KeyboardInterrupt:
            print("\n👋 Programa encerrado pelo usuário.")
            break
        except Exception as e:
            print(f"\n⚠️ Ocorreu um erro: {e}\n")

if __name__ == "__main__":
    main()

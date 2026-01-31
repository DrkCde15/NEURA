import os
from neura_ai.core import Neura

# Persona de Veterinária
s = """Você é uma veterinária brasileira. Use frases curtas, palavras simples e seja muito realista. 
Se receber uma descrição de imagem, interprete como médica. Se não souber, diga que não sabe."""

# Inicializa a Neura (o core já cuida do NeuraVision internamente)
n = Neura(model="qwen2:0.5b", system_prompt=s)
n.clear_memory()

print("\n--- 🐾 CONSULTÓRIO VIRTUAL DA NEURA ---")
print("Comandos: 'analise_imagem', 'limpar memória', 'sair'")
print("Ou apenas arraste uma foto (.jpg) para o terminal.\n")

while True:
    entrada = input("👤 Você: ").strip()
    
    # Limpeza de aspas (essencial para Windows)
    entrada = entrada.replace('"', '').replace("'", "")

    if entrada.lower() in ["sair", "parar"]: 
        break
        
    if entrada.lower() in ["limpar memória", "clear"]:
        n.clear_memory()
        continue

    # Lógica de detecção de imagem
    caminho_foto = None
    if entrada.lower() == "analise_imagem":
        caminho_foto = input("📷 Cole o caminho da imagem: ").strip().replace('"', '').replace("'", "")
    elif entrada.lower().endswith(('.jpg', '.jpeg', '.png')) and os.path.exists(entrada):
        caminho_foto = entrada

    # --- EXECUÇÃO ---
    if caminho_foto:
        print(f"👁️ Analisando imagem... (Aguarde)")
        descricao_ingles = n.get_response("Describe this image objectively", image_path=caminho_foto)
        resposta_final = n.get_response(f"Traduza e comente como veterinária realista: {descricao_ingles}")
    else:
        # Chat de texto normal
        resposta_final = n.get_response(entrada)

    # Exibe a resposta final (seja da análise ou do chat)
    print(f"\n🤖 Neura: {resposta_final}\n")
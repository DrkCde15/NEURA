from neura_ai import Neura

# 1. Definimos a personalidade
s = """Você é uma veterinária brasileira. Use frases curtas, palavras simples e seja muito realista. 
Não invente palavras. Se não souber algo, diga que não sabe."""

# 2. Criamos a instância com o modelo leve e o prompt definido
n = Neura(
    model="qwen2:0.5b", 
    system_prompt=s
)

m = n.list_models()

# Opcional: Limpar memória ao iniciar para um novo atendimento limpo
n.clear_memory()

print("\n--- INICIANDO CHAT ---")
print("(Digite 'sair' para encerrar)\n")

while True:
    # Captura a entrada do usuário
    entrada = input("👤 Você: ")
    
    # Listar modelos disponíveis
    if entrada.lower() in ["listar modelos", "list models", "modelos"]:
        m = n.list_models()
        print("Modelos disponíveis:", m)
        continue
    
    # Condição de limpesa de memória
    if entrada.lower() in ["limpar memória", "limpar memoria", "clear memory"]:
        n.clear_memory()
        print("\n🤖 Neura: Memória limpa. Podemos começar um novo atendimento!\n")
        continue

    # Condição de saída
    if entrada.lower() in ["sair", "exit", "parar"]:
        print("\n🤖 Neura: Atendimento finalizado. Até logo!")
        break

    # Obtém a resposta da sua biblioteca
    resposta = n.get_response(entrada)
    
    # Exibe a resposta
    print(f"\n🤖 Neura: {resposta}\n")
import ollama
import sqlite3
import pyfiglet

# --------------------------
# CONFIG
# --------------------------
DB_PATH = "data_memory.db"
MODEL = "gemma:2b"  # Altere para o modelo que você tem localmente

# --------------------------
# INICIALIZAÇÃO
# --------------------------
def display_banner():
    banner = pyfiglet.figlet_format("NEURA AI", font="small")
    print("=" * 60)
    print(banner)
    print("🤖  Assistente IA com Memória Local")

def display_help():
    """Exibe os comandos disponíveis de forma organizada"""
    print("\n" + "📋 COMANDOS DISPONÍVEIS ".center(50, "="))
    print("🔸 'sair'    - Encerra o programa")
    print("🔸 'limpar'  - Limpa toda a memória da conversa")
    print("🔸 'estado'  - Mostra estatísticas da memória")
    print("🔸 'ajuda'   - Mostra esta mensagem")
    print("=" * 50 + "\n")

# --------------------------
# FUNÇÕES DE MEMÓRIA
# --------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_message(role, content):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO memory (role, content) VALUES (?, ?)", (role, content))
    conn.commit()
    conn.close()

def load_memory(limit=3):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT role, content FROM memory ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows[::-1]

def clear_memory():
    """Limpa toda a memória do banco de dados"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM memory")
    conn.commit()
    conn.close()
    print("🗑️  Memória limpa com sucesso!\n")

def get_memory_stats():
    """Retorna estatísticas detalhadas da memória"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Total de mensagens
    cur.execute("SELECT COUNT(*) FROM memory")
    total = cur.fetchone()[0]
    
    # Mensagens por role
    cur.execute("SELECT role, COUNT(*) FROM memory GROUP BY role")
    role_counts = dict(cur.fetchall())
    
    # Última mensagem
    cur.execute("SELECT timestamp FROM memory ORDER BY id DESC LIMIT 1")
    last_msg = cur.fetchone()
    
    conn.close()
    
    return {
        'total': total,
        'user_messages': role_counts.get('user', 0),
        'assistant_messages': role_counts.get('assistant', 0),
        'last_message': last_msg[0] if last_msg else 'Nenhuma'
    }

# --------------------------
# CHAMADA AO OLLAMA
# --------------------------
def call_ollama(prompt):
    try:
        response = ollama.generate(model=MODEL, prompt=prompt)
        return response['response']
    except Exception as e:
        return f"❌ Erro ao chamar o modelo: {str(e)}"

# --------------------------
# LOOP PRINCIPAL
# --------------------------
def main():
    # Exibe banner inicial
    display_banner()
    
    init_db()
    
    # Mostra estado inicial da memória
    stats = get_memory_stats()
    print(f"📊 Memória Inicial: {stats['total']} mensagens")
    print(f"👤 Você: {stats['user_messages']} | 🤖 Neura: {stats['assistant_messages']}")
    print("─" * 50)
    
    display_help()

    while True:
        user_msg = input("💬 Você: ").strip()
        
        # Comando para sair
        if user_msg.lower() in ["sair", "exit", "quit", "quit()"]:
            print("\n👋 Até mais! Encerrando Neura AI...")
            break
        
        # Comando para limpar memória
        elif user_msg.lower() in ["limpar", "clear", "reset"]:
            clear_memory()
            continue
        
        # Comando para mostrar estado da memória
        elif user_msg.lower() in ["estado", "status", "memória", "memory", "stats"]:
            stats = get_memory_stats()
            print("\n" + "📊 ESTADO DA MEMÓRIA ".center(50, "─"))
            print(f"📈 Total de mensagens: {stats['total']}")
            print(f"👤 Suas mensagens: {stats['user_messages']}")
            print(f"🤖 Respostas da Neura: {stats['assistant_messages']}")
            print(f"🕒 Última mensagem: {stats['last_message']}")
            print("─" * 50 + "\n")
            continue
        
        # Comando para ajuda
        elif user_msg.lower() in ["ajuda", "help", "comandos", "?"]:
            display_help()
            continue

        # Processa mensagem normal do usuário
        save_message("user", user_msg)

        # Recupera memória curta
        memory_blocks = load_memory(limit=3)
        
        SYSTEM_MESSAGE = (
            "Você é a Neura, um assistente IA conversando em português brasileiro. "
            "Seja claro, natural e prestativo. Responda sempre em português."
        )

        # Monta prompt com contexto - CORRIGIDO
        full_prompt = f"CONTEXTO DO SISTEMA: {SYSTEM_MESSAGE}\n"
        full_prompt += "HISTÓRICO RECENTE DA CONVERSA:\n"
        for role, content in memory_blocks:
            full_prompt += f"{role.upper()}: {content}\n"
        full_prompt += f"USER: {user_msg}\nASSISTANT: "

        # Chama modelo
        print("🤖 Neura: ", end="", flush=True)
        bot_response = call_ollama(full_prompt)
        print(bot_response + "\n")

        # Salva resposta
        save_message("assistant", bot_response)

if __name__ == "__main__":
    main()
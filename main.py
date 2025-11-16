import ollama
import sqlite3
import pyfiglet
import speech_recognition as sr
import pyttsx3

# --------------------------
# CONFIG
# --------------------------
DB_PATH = "data_memory.db"
MODEL = "gemma:2b"  # modelo no Ollama

# --------------------------
# TTS (Síntese de Voz)
# --------------------------
def init_tts():
    engine = pyttsx3.init()
    engine.setProperty("rate", 185)
    engine.setProperty("volume", 1.0)

    # Seleciona voz PT-BR se existir
    for voice in engine.getProperty("voices"):
        if "brazil" in voice.name.lower() or "portuguese" in voice.name.lower():
            engine.setProperty("voice", voice.id)
            break

    return engine

tts_engine = init_tts()

def speak(text):
    tts_engine.say(text)
    tts_engine.runAndWait()

# --------------------------
# MODO DE VOZ CONTÍNUO
# --------------------------
def listen_voice_continuous():
    recognizer = sr.Recognizer()

    print("\n🎤 MODO DE VOZ ATIVADO")
    print("Diga algo... (fale 'parar', 'sair' ou 'cancelar' para encerrar)\n")

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)

        while True:
            try:
                print("🎧 Ouvindo...")
                audio = recognizer.listen(source)

                text = recognizer.recognize_google(audio, language="pt-BR")
                print(f"🗣️ Você disse: {text}")

                # Palavra de parada
                if text.lower().strip() in ["parar", "sair", "cancelar", "stop"]:
                    print("🛑 Modo de voz encerrado.\n")
                    return

                yield text

            except sr.UnknownValueError:
                print("❌ Não entendi, tente novamente.")
            except sr.RequestError:
                print("❌ Erro no serviço de reconhecimento.")
                return

# --------------------------
# INTERFACE
# --------------------------
def display_banner():
    banner = pyfiglet.figlet_format("NEURA AI", font="small")
    print("=" * 60)
    print(banner)
    print("🤖  Assistente IA com Memória Local")

def display_help():
    print("\n" + "📋 COMANDOS DISPONÍVEIS ".center(50, "="))
    print("🔸 'sair'    - Encerra o programa")
    print("🔸 'limpar'  - Limpa a memória")
    print("🔸 'estado'  - Mostra estatísticas")
    print("🔸 'ajuda'   - Mostra ajuda")
    print("🔸 'voz'     - Ativa o modo de voz contínuo")
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
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM memory")
    conn.commit()
    conn.close()
    print("🗑️  Memória limpa!\n")

def get_memory_stats():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM memory")
    total = cur.fetchone()[0]

    cur.execute("SELECT role, COUNT(*) FROM memory GROUP BY role")
    role_counts = dict(cur.fetchall())

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
        return response["response"]
    except Exception as e:
        return f"❌ Erro ao chamar modelo: {e}"

# --------------------------
# LOOP PRINCIPAL
# --------------------------
def main():
    display_banner()
    init_db()

    stats = get_memory_stats()
    print(f"📊 Memória Inicial: {stats['total']} mensagens")
    print(f"👤 Você: {stats['user_messages']} | 🤖 Neura: {stats['assistant_messages']}")
    print("─" * 50)

    display_help()

    while True:
        user_msg = input("💬 Você: ").strip()

        # comando sair
        if user_msg.lower() in ["sair", "exit", "quit"]:
            print("\n👋 Encerrando Neura AI...")
            break

        # limpar memória
        elif user_msg.lower() in ["limpar", "clear"]:
            clear_memory()
            continue

        # estado da memória
        elif user_msg.lower() in ["estado", "status", "memory", "stats"]:
            stats = get_memory_stats()
            print("\n" + "📊 ESTADO DA MEMÓRIA ".center(50, "─"))
            print(f"📈 Total: {stats['total']}")
            print(f"👤 Usuário: {stats['user_messages']}")
            print(f"🤖 IA: {stats['assistant_messages']}")
            print(f"🕒 Última: {stats['last_message']}")
            print("─" * 50 + "\n")
            continue

        # ajuda
        elif user_msg.lower() in ["ajuda", "help", "?"]:
            display_help()
            continue

        # MODO DE VOZ CONTÍNUO
        elif user_msg.lower() in ["voz", "voice", "mic"]:
            for spoken_text in listen_voice_continuous():
                user_msg = spoken_text

                save_message("user", user_msg)
                memory_blocks = load_memory(limit=3)

                SYSTEM_MESSAGE = (
                    "Você é a Neura, um assistente IA brasileiro, direto, claro e prestativo. "
                    "Responda sempre em português."
                )

                # prompt
                full_prompt = f"CONTEXTO DO SISTEMA: {SYSTEM_MESSAGE}\n"
                full_prompt += "HISTÓRICO:\n"
                for role, content in memory_blocks:
                    full_prompt += f"{role.upper()}: {content}\n"
                full_prompt += f"USER: {user_msg}\nASSISTANT: "

                print("🤖 Neura: ", end="", flush=True)
                bot_response = call_ollama(full_prompt)
                print(bot_response + "\n")

                speak(bot_response)
                save_message("assistant", bot_response)

            continue  # volta ao terminal após encerrar modo voz

        # fluxo normal (texto)
        save_message("user", user_msg)

        memory_blocks = load_memory(limit=3)

        SYSTEM_MESSAGE = (
            "Você é a Neura, um assistente IA brasileiro, direto, claro e prestativo. "
            "Responda sempre em português."
        )

        full_prompt = f"CONTEXTO DO SISTEMA: {SYSTEM_MESSAGE}\n"
        full_prompt += "HISTÓRICO:\n"
        for role, content in memory_blocks:
            full_prompt += f"{role.upper()}: {content}\n"
        full_prompt += f"USER: {user_msg}\nASSISTANT: "

        print("🤖 Neura: ", end="", flush=True)
        bot_response = call_ollama(full_prompt)
        print(bot_response + "\n")

        speak(bot_response)
        save_message("assistant", bot_response)

if __name__ == "__main__":
    main()

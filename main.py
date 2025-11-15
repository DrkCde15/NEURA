import os
import sqlite3
import requests
import threading
import flet as ft

# -------- CONFIG --------
OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", "http://localhost:11434/api/generate")
DB_PATH = os.path.join(os.path.dirname(__file__), "data_memory.db")
MODEL_TEXT = os.environ.get("MODEL_TEXT", "gemma:2b")
MEMORY_LIMIT = 3
MAX_TOKENS = 256

# -------- MEMÓRIA (SQLite) THREAD-SAFE --------
class MemoryDB:
    def __init__(self, path=DB_PATH):
        self.path = path
        self.lock = threading.Lock()
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with self.lock:
            conn = sqlite3.connect(self.path, check_same_thread=False)
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT,
                    content TEXT
                )
            """)
            conn.commit()
            conn.close()

    def save_message(self, role, content):
        with self.lock:
            conn = sqlite3.connect(self.path, check_same_thread=False)
            c = conn.cursor()
            c.execute("INSERT INTO memory (role, content) VALUES (?, ?)", (role, content))
            conn.commit()
            conn.close()

    def get_recent(self, limit=MEMORY_LIMIT):
        with self.lock:
            conn = sqlite3.connect(self.path, check_same_thread=False)
            c = conn.cursor()
            c.execute("SELECT role, content FROM memory ORDER BY id DESC LIMIT ?", (limit,))
            rows = c.fetchall()
            conn.close()
            return rows[::-1]

    def clear(self):
        with self.lock:
            conn = sqlite3.connect(self.path, check_same_thread=False)
            c = conn.cursor()
            c.execute("DELETE FROM memory")
            conn.commit()
            conn.close()

# -------- CLIENTE OLLAMA --------
class OllamaClient:
    def __init__(self, api_url=OLLAMA_API_URL):
        self.api_url = api_url.rstrip("/")

    def generate_text(self, model, prompt, max_tokens=MAX_TOKENS):
        payload = {
            "model": model,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": 0.2,
            "stream": False  # 🔥 EVITA O ERRO “Extra data”
        }

        try:
            resp = requests.post(self.api_url, json=payload, timeout=60)
            resp.raise_for_status()

            data = resp.json()  # AGORA SÓ VEM UM JSON
            return data.get("response", "").strip() or resp.text

        except Exception as e:
            if "memory" in str(e).lower():
                return "[Erro: modelo não pôde ser carregado. Use modelo mais leve ou reduza histórico/prompt]"
            return f"[Erro na geração: {e}]"

# -------- INTERFACE (Flet) --------
def main(page: ft.Page):
    page.title = "NEURA - Chatbot Offline"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window_width = 900
    page.window_height = 700

    db = MemoryDB()
    client = OllamaClient()

    chat_view = ft.ListView(expand=True, spacing=10, auto_scroll=True)

    input_field = ft.TextField(
        hint_text="Digite sua mensagem...",
        expand=True,
        autofocus=True,
        on_submit=lambda e: send_message()
    )

    send_btn = ft.ElevatedButton("Enviar", on_click=lambda e: send_message())
    clear_btn = ft.OutlinedButton("Limpar Memória", on_click=lambda e: clear_memory())
    refresh_btn = ft.OutlinedButton("Atualizar Histórico", on_click=lambda e: load_history())

    button_row = ft.Row([input_field, send_btn], alignment=ft.MainAxisAlignment.START)
    control_row = ft.Row([clear_btn, refresh_btn])

    def append_ui(role, content):
        color = "#1e88e5" if role.lower().startswith("vo") else "#43a047"
        chat_view.controls.append(
            ft.Container(
                content=ft.Text(f"{role}: {content}", selectable=True),
                padding=10,
                bgcolor=color + "20",
                border_radius=10
            )
        )
        page.update()

    def load_history():
        chat_view.controls.clear()
        rows = db.get_recent(limit=1000)
        for role, content in rows:
            append_ui(role, content)

    def build_context():
        rows = db.get_recent(limit=MEMORY_LIMIT)
        contexto = ""
        for role, content in rows:
            if role.lower().startswith('usu'):
                contexto += f"Usuário: {content}\n"
            else:
                contexto += f"IA: {content}\n"
        return contexto

    def generate_and_append(user_text):
        contexto = build_context()
        full_prompt = f"{contexto}\nUsuário: {user_text}\nIA:"
        resposta = client.generate_text(MODEL_TEXT, full_prompt)

        db.save_message('IA', resposta)
        append_ui('IA', resposta)
        page.update()

    def send_message():
        user_text = input_field.value.strip()
        if not user_text:
            return

        input_field.value = ""
        append_ui("Você", user_text)
        db.save_message("Usuário", user_text)
        page.update()

        threading.Thread(target=generate_and_append, args=(user_text,), daemon=True).start()

    def clear_memory():
        db.clear()
        chat_view.controls.clear()
        append_ui("Sistema", "Memória limpa.")

    load_history()

    page.add(
        ft.Column(
            [
                ft.Text("💬 LocalMind Chatbot", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                chat_view,
                ft.Divider(),
                button_row,
                control_row
            ],
            expand=True
        )
    )

# -------- RUN APP --------
if __name__ == "__main__":
    ft.app(target=main)

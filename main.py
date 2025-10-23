import os
import sqlite3
import requests
import threading
from tkinter import Tk, Text, Entry, Button, Label, END, Scrollbar, RIGHT, Y, LEFT, BOTH, Frame

# -------- CONFIGURAÇÃO --------
OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", "http://localhost:11434/v1/completions")
DB_PATH = os.path.join(os.path.dirname(__file__), "data_memory.db")
MODEL_TEXT = os.environ.get("MODEL_TEXT", "phi3")
MEMORY_LIMIT = 10  # quantas trocas recuperar como contexto

# -------- MEMÓRIA (SQLite) --------
class MemoryDB:
    def __init__(self, path=DB_PATH):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True) 
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS memory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        role TEXT,
                        content TEXT
                    )''')
        conn.commit()
        conn.close()

    def save_message(self, role, content):
        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        c.execute("INSERT INTO memory (role, content) VALUES (?, ?)", (role, content))
        conn.commit()
        conn.close()

    def get_recent(self, limit=MEMORY_LIMIT):
        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        c.execute("SELECT role, content FROM memory ORDER BY id DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        conn.close()
        # retorna na ordem cronológica
        return rows[::-1]

    def clear(self):
        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        c.execute("DELETE FROM memory")
        conn.commit()
        conn.close()

# -------- CLIENTE OLLAMA (simples, via HTTP) --------
class OllamaClient:
    def __init__(self, api_url=OLLAMA_API_URL):
        self.api_url = api_url.rstrip("/")

    def generate_text(self, model, prompt, max_tokens=512):
        payload = {
            "model": model,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": 0.2
        }
        try:
            resp = requests.post(self.api_url, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            # Corrige leitura da resposta
            return data.get("choices", [{}])[0].get("text", "").strip() or resp.text
        except Exception as e:
            return f"[Erro na geração: {e}]"

# -------- GUI --------
class LocalMindGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LocalMind - Chatbot Offline")
        self.root.geometry("900x700")

        self.db = MemoryDB()
        self.client = OllamaClient()

        self._build_ui()
        self._load_history_to_ui()

    def _build_ui(self):
        top_frame = Frame(self.root)
        top_frame.pack(fill=BOTH, expand=True)

        # Chat text box com scrollbar
        self.text_box = Text(top_frame, wrap='word', state='normal')
        self.text_box.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar = Scrollbar(top_frame, command=self.text_box.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.text_box.config(yscrollcommand=scrollbar.set)

        # Input e botões
        bottom_frame = Frame(self.root)
        bottom_frame.pack(fill='x')

        self.entry = Entry(bottom_frame)
        self.entry.pack(side=LEFT, fill='x', expand=True, padx=6, pady=6)
        self.entry.bind('<Return>', lambda e: self._on_send())

        send_btn = Button(bottom_frame, text='Enviar', command=self._on_send)
        send_btn.pack(side=LEFT, padx=6)

        clear_btn = Button(bottom_frame, text='Limpar Memória', command=self._on_clear_memory)
        clear_btn.pack(side=LEFT, padx=6)

        refresh_btn = Button(bottom_frame, text='Atualizar Histórico', command=self._load_history_to_ui)
        refresh_btn.pack(side=LEFT, padx=6)

        # Área para visualizar imagem carregada
        self.img_label = Label(self.root)
        self.img_label.pack(pady=6)

    def _append_ui(self, who, text):
        tag = f"{who}: "
        self.text_box.insert(END, tag + text + "\n\n")
        self.text_box.see(END)

    def _load_history_to_ui(self):
        self.text_box.delete(1.0, END)
        rows = self.db.get_recent(limit=1000)
        for role, content in rows:
            self.text_box.insert(END, f"{role}: {content}\n\n")
        self.text_box.see(END)

    def _on_send(self):
        user_text = self.entry.get().strip()
        if not user_text:
            return
        self.entry.delete(0, END)
        self._append_ui('Você', user_text)
        self.db.save_message('Usuário', user_text)

        # Geração em thread pra não travar UI
        threading.Thread(target=self._generate_and_append, args=(user_text,)).start()

    def _generate_and_append(self, user_text):
        contexto = self._build_context()
        full_prompt = contexto + "\nUsuário: " + user_text + "\nIA:"
        resposta = self.client.generate_text(MODEL_TEXT, full_prompt)
        self.db.save_message('IA', resposta)
        self._append_ui('IA', resposta)

    def _build_context(self):
        rows = self.db.get_recent(limit=MEMORY_LIMIT)
        contexto = ""
        for role, content in rows:
            if role.lower().startswith('usu'):
                contexto += f"Usuário: {content}\n"
            else:
                contexto += f"IA: {content}\n"
        return contexto

    def _on_clear_memory(self):
        self.db.clear()
        self._load_history_to_ui()
        self._append_ui('Sistema', 'Memória limpa.')

# -------- RODAR APP --------
if __name__ == '__main__':
    # Verificações básicas
    print("Inicializando LocalMind GUI...")
    root = Tk()
    app = LocalMindGUI(root)
    root.mainloop()
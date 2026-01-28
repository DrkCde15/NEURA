import ollama
import sqlite3

class Neura:
    def __init__(self, db_path="data_memory.db", model="gemma:2b"):
        self.db_path = db_path
        self.model = model
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT, 
                    content TEXT, 
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def save_message(self, role, content):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO memory (role, content) VALUES (?, ?)", (role, content))

    def load_memory(self, limit=3):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT role, content FROM memory ORDER BY id DESC LIMIT ?", (limit,))
            return cur.fetchall()[::-1]

    def clear_memory(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM memory")

    def get_response(self, user_msg):
        memory_blocks = self.load_memory(limit=3)
        system_prompt = "Você é a Neura, assistente brasileira, direta e clara. Responda em português."
        
        full_prompt = f"SYSTEM: {system_prompt}\nHISTORY:\n"
        for role, content in memory_blocks:
            full_prompt += f"{role.upper()}: {content}\n"
        full_prompt += f"USER: {user_msg}\nASSISTANT: "

        try:
            response = ollama.generate(model=self.model, prompt=full_prompt)
            return response["response"]
        except Exception as e:
            return f"Erro no Ollama: {e}"
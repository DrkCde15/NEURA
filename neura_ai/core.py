import ollama
import sqlite3

class Neura:
    def __init__(self, db_path="data_memory.db", model="qwen2:0.5b", system_prompt=None):
        """
        Inicializa a Neura com modelo, banco de dados e prompt de sistema.
        """
        self.db_path = db_path
        self.model = model
        # Define o prompt padrão caso o usuário não passe um personalizado
        self.default_system = system_prompt or "Você é a Neura, assistente brasileira, direta e clara. Responda em português."
        self._init_db()

    def _init_db(self):
        """Cria a tabela de memória se ela não existir."""
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
        """Registra uma interação no banco de dados local."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO memory (role, content) VALUES (?, ?)", (role, content))

    def load_memory(self, limit=3):
        """Recupera o histórico recente para dar contexto à IA."""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT role, content FROM memory ORDER BY id DESC LIMIT ?", (limit,))
            return cur.fetchall()[::-1]

    def clear_memory(self):
        """Limpa todo o histórico de conversas do banco de dados."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM memory")
            print("🧠 Memória resetada para um novo atendimento!")

    def models_list(self):
        """Lista todos os modelos instalados no Ollama local."""
        try:
            models_data = ollama.list()
            if hasattr(models_data, 'models'):
                return [m.model for m in models_data.models]
            if isinstance(models_data, dict) and 'models' in models_data:
                return [m.get('model', m.get('name', 'Desconhecido')) for m in models_data['models']]
            return ["Nenhum modelo encontrado."]
        except Exception as e:
            return [f"Erro ao listar modelos: {e}"]

    def get_response(self, user_msg, custom_prompt=None):
            memory_blocks = self.load_memory(limit=3)
            active_prompt = custom_prompt or self.default_system
            
            full_prompt = f"SYSTEM: {active_prompt}\nHISTORY:\n"
            for role, content in memory_blocks:
                full_prompt += f"{role.upper()}: {content}\n"
            full_prompt += f"USER: {user_msg}\nASSISTANT: "

            try:
                # Adicionamos 'options' para estabilizar a inteligência da IA
                response = ollama.generate(
                    model=self.model, 
                    prompt=full_prompt,
                    options={
                        "temperature": 0.1,  # Quase zero criatividade, foco total em fatos
                        "top_p": 0.9,         # Limita o vocabulário às palavras mais prováveis
                        "stop": ["USER:", "SYSTEM:"] # Garante que ela não tente falar por você
                    }
                )
                final_text = response["response"]
                self.save_message("user", user_msg)
                self.save_message("assistant", final_text)
                return final_text

            except Exception as e:
                err_msg = str(e).lower()
                if "memory" in err_msg or "available" in err_msg or "500" in err_msg:
                    return f"⚠️ ERRO: O modelo '{self.model}' é muito pesado para sua RAM atual."
                return f"❌ Erro técnico: {e}"
import os
import sqlite3
import ollama
from .image import NeuraVision  # Importa o novo módulo especializado

class Neura:
    def __init__(self, model="qwen2:0.5b", vision_model="moondream", system_prompt=""):
        self.model = model
        self.vision_model = vision_model
        self.system_prompt = system_prompt
        self.db_path = "data_memory.db"
        
        # Inicializa o especialista em visão
        self.vision = NeuraVision(model=self.vision_model)
        
        # Inicializa o banco de dados
        self._init_db()

    def _init_db(self):
        """Cria a tabela de memória se não existir."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT,
                    content TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def save_message(self, role, content):
        """Salva uma mensagem no histórico do SQLite."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO memory (role, content) VALUES (?, ?)', (role, content))
            conn.commit()

    def get_context(self, limit=5):
        """Recupera as últimas mensagens para manter o contexto."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT role, content FROM memory ORDER BY id DESC LIMIT ?', (limit,))
            rows = cursor.fetchall()
            
            context = [{"role": "system", "content": self.system_prompt}]
            # Inverte para manter a ordem cronológica
            for role, content in reversed(rows):
                context.append({"role": role, "content": content})
            return context

    def clear_memory(self):
        """Limpa o histórico de conversas."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM memory')
            conn.commit()
        print("🧠 Memória resetada!")

    def list_models(self):
        """Lista os modelos disponíveis no Ollama local."""
        models_info = ollama.list()
        return [m['name'] for m in models_info['models']]

    def get_response(self, user_msg, image_path=None):
        """Garante a resposta da IA, decidindo entre Texto ou Visão."""
        try:
            # FLUXO 1: VISÃO (Se houver imagem, delega ao NeuraVision)
            if image_path and os.path.exists(image_path):
                print(f"Modo Visão ativado...")
                # O módulo image.py resolve o processamento pesado
                analise = self.vision.process_and_analyze(image_path, user_msg)
                
                # Salva a análise na memória para o contexto futuro
                if analise:
                    self.save_message("assistant", f"[🔍 Visão]: {analise}")
                return analise

            # FLUXO 2: TEXTO (Qwen)
            self.save_message("user", user_msg)
            contexto = self.get_context()

            response = ollama.chat(
                model=self.model,
                messages=contexto,
                options={"temperature": 0.3} # Baixa temperatura = Respostas mais realistas
            )

            final_text = response['message']['content'].strip()
            
            if final_text:
                self.save_message("assistant", final_text)
                return final_text
            
            return "⚠️ Neura: Não consegui gerar uma resposta no momento."

        except Exception as e:
            return f"❌ Erro no Core: {str(e)}"
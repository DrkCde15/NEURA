import os
import sqlite3
import logging
import requests
from typing import List, Optional, Dict
import ollama
from .image import NeuraVision
from .config import NeuraConfig

# Configuração de Logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("NeuraCore")

# Silencia logs verbosos de bibliotecas de terceiros
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

class Neura:
    def __init__(self, model: str = NeuraConfig.LLM_MODEL, 
                 vision_model: str = NeuraConfig.VISION_MODEL, 
                 system_prompt: str = "",
                 host: str = NeuraConfig.OLLAMA_BASE_URL,
                 headers: Optional[Dict[str, str]] = None,
                 use_memory: bool = True):
        self.model = model
        self.vision_model = vision_model
        self.system_prompt = system_prompt
        self.db_path = NeuraConfig.DB_PATH
        self.host = host
        self.use_memory = use_memory
        
        # Se estiver usando o túnel da Neura, adiciona os headers de bypass automaticamente
        self.headers = headers or {}
        if self.host == NeuraConfig.TUNNEL_URL:
            self.headers.update(NeuraConfig.BYPASS_HEADERS)
        
        # Inicializa o especialista em visão com host e headers
        self.vision = NeuraVision(model=self.vision_model, host=self.host, headers=self.headers)
        
        # Inicializa o cliente Ollama com suporte a headers
        try:
            self.client = ollama.Client(host=self.host, headers=self.headers)
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente Ollama: {e}")
            self.client = None
        
        # Inicializa o banco de dados se a memória estiver ativa
        if self.use_memory:
            self._init_db()

    def health_check(self) -> bool:
        """Verifica se o servidor de IA no host configurado está acessível."""
        try:
            # Tenta conectar no host atual (pode ser local ou túnel)
            response = requests.get(f"{self.host}/api/tags", headers=self.headers, timeout=5)
            return response.status_code == 200
        except Exception:
            return False


    def _init_db(self) -> None:
        """Cria a tabela de memória se não existir."""
        if not self.use_memory:
            return
        try:
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
        except sqlite3.Error as e:
            logger.critical(f"Erro ao inicializar banco de dados: {e}")

    def save_message(self, role: str, content: str) -> None:
        """Salva uma mensagem no histórico do SQLite."""
        if not self.use_memory:
            return
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO memory (role, content) VALUES (?, ?)', (role, content))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Erro ao salvar mensagem: {e}")

    def get_context(self, limit: int = 5) -> List[Dict[str, str]]:
        """Recupera as últimas mensagens para manter o contexto."""
        if not self.use_memory:
             return [{"role": "system", "content": self.system_prompt}] if self.system_prompt else []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT role, content FROM memory ORDER BY id DESC LIMIT ?', (limit,))
                rows = cursor.fetchall()
                
                context = []
                if self.system_prompt:
                    context.append({"role": "system", "content": self.system_prompt})
                
                # Inverte para manter a ordem cronológica
                for role, content in reversed(rows):
                    context.append({"role": role, "content": content})
                return context
        except sqlite3.Error as e:
            logger.error(f"Erro ao recuperar contexto: {e}")
            return [{"role": "system", "content": self.system_prompt}]

    def clear_memory(self) -> None:
        """Limpa o histórico de conversas."""
        if not self.use_memory:
            print("Memória SQLite desativada nesta instância.")
            return
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM memory')
                conn.commit()
            logger.info("Memória resetada com sucesso.")
            print("Memória resetada!")
        except sqlite3.Error as e:
            logger.error(f"Erro ao limpar memória: {e}")

    def list_models(self) -> List[str]:
        """Lista os modelos disponíveis no Ollama local."""
        try:
            if not self.client:
                return []
            models_info = self.client.list()
            # Suporte para objetos Response do Ollama (versões mais recentes)
            if hasattr(models_info, 'models'):
                return [m.model for m in models_info.models]
            # Fallback para dicionário (versões antigas)
            return [m['name'] for m in models_info.get('models', [])]
        except Exception as e:
            logger.error(f"Erro ao listar modelos: {e}")
            return []

    def get_response(self, user_msg: str, image_path: Optional[str] = None, 
                     history: Optional[List[Dict[str, str]]] = None) -> str:
        """Garante a resposta da IA, decidindo entre Texto ou Visão."""
        try:
            # FLUXO 1: VISÃO (Se houver imagem, delega ao NeuraVision)
            if image_path and os.path.exists(image_path):
                logger.info(f"Iniciando modo visão para: {image_path}")
                print(f"Modo Visão ativado...")
                analise = self.vision.process_and_analyze(image_path, user_msg)
                
                if analise and self.use_memory:
                    self.save_message("assistant", f"[🔍 Visão]: {analise}")
                return analise

            # FLUXO 2: TEXTO
            if history:
                # Se o usuário passou um histórico externo (ex: MySQL), usa ele
                contexto = history
                # Garante que o system prompt esteja no topo se não estiver
                if self.system_prompt and (not contexto or contexto[0].get("role") != "system"):
                    contexto.insert(0, {"role": "system", "content": self.system_prompt})
                contexto.append({"role": "user", "content": user_msg})
            elif self.use_memory:
                # Usa o fluxo padrão do SQLite
                self.save_message("user", user_msg)
                contexto = self.get_context()
            else:
                # Fluxo stateless: Apenas prompt de sistema + mensagem atual
                contexto = []
                if self.system_prompt:
                    contexto.append({"role": "system", "content": self.system_prompt})
                contexto.append({"role": "user", "content": user_msg})

            logger.info(f"Enviando prompt para LLM: {self.model}")
            response = self.client.chat(
                model=self.model,
                messages=contexto,
                options={"temperature": 0.3}
            )

            final_text = response['message']['content'].strip()
            
            if final_text:
                if self.use_memory:
                    self.save_message("assistant", final_text)
                return final_text
            
            return "Neura: Não consegui gerar uma resposta no momento."

        except Exception as e:
            logger.error(f"Erro crítico no Core: {e}", exc_info=True)
            return f"Erro no Core: {str(e)}"
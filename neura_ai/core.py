import logging
import os
import sqlite3
from typing import Dict, List, Optional

import requests

from .config import NeuraConfig
from .image import NeuraVision

# Logging configuration
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("NeuraCore")


class Neura:
    def __init__(
        self,
        model: str = NeuraConfig.LLM_MODEL,
        vision_model: str = NeuraConfig.VISION_MODEL,
        system_prompt: str = "",
        host: str = NeuraConfig.GROQ_API_BASE_URL,
        headers: Optional[Dict[str, str]] = None,
        use_memory: bool = True,
    ):
        self.model = model
        self.vision_model = vision_model
        self.system_prompt = system_prompt
        self.db_path = NeuraConfig.DB_PATH
        self.use_memory = use_memory

        # Kept as `host` for backward compatibility with previous API.
        self.api_base_url = host.rstrip("/") if host else NeuraConfig.GROQ_API_BASE_URL
        self.chat_url = f"{self.api_base_url}/chat/completions"
        self.models_url = NeuraConfig.GROQ_MODELS_URL

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {NeuraConfig.GROQ_API_KEY}",
        }
        if headers:
            self.headers.update(headers)

        self.vision = NeuraVision(
            model=self.vision_model,
            api_base_url=self.api_base_url,
            headers=self.headers,
        )

        if self.use_memory:
            self._init_db()

    def health_check(self) -> bool:
        """Verifica se a API Groq esta acessivel."""
        if not NeuraConfig.GROQ_API_KEY:
            return False

        try:
            response = requests.get(
                self.models_url,
                headers=self.headers,
                timeout=NeuraConfig.REQUEST_TIMEOUT,
            )
            return response.status_code == 200
        except Exception:
            return False

    def _init_db(self) -> None:
        """Cria a tabela de memoria se nao existir."""
        if not self.use_memory:
            return
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    '''
                    CREATE TABLE IF NOT EXISTS memory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        role TEXT,
                        content TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                    '''
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.critical(f"Erro ao inicializar banco de dados: {e}")

    def save_message(self, role: str, content: str) -> None:
        """Salva uma mensagem no historico do SQLite."""
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
        """Recupera as ultimas mensagens para manter o contexto."""
        if not self.use_memory:
            return [{"role": "system", "content": self.system_prompt}] if self.system_prompt else []

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT role, content FROM memory ORDER BY id DESC LIMIT ?', (limit,))
                rows = cursor.fetchall()

                context: List[Dict[str, str]] = []
                if self.system_prompt:
                    context.append({"role": "system", "content": self.system_prompt})

                for role, content in reversed(rows):
                    context.append({"role": role, "content": content})
                return context
        except sqlite3.Error as e:
            logger.error(f"Erro ao recuperar contexto: {e}")
            return [{"role": "system", "content": self.system_prompt}] if self.system_prompt else []

    def clear_memory(self) -> None:
        """Limpa o historico de conversas."""
        if not self.use_memory:
            print("Memoria SQLite desativada nesta instancia.")
            return

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM memory')
                conn.commit()
            logger.info("Memoria resetada com sucesso.")
            print("Memoria resetada!")
        except sqlite3.Error as e:
            logger.error(f"Erro ao limpar memoria: {e}")

    def list_models(self) -> List[str]:
        """Lista os modelos disponiveis na Groq API."""
        if not NeuraConfig.GROQ_API_KEY:
            return []

        try:
            response = requests.get(
                self.models_url,
                headers=self.headers,
                timeout=NeuraConfig.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            payload = response.json()
            data = payload.get("data", [])
            return [item.get("id") for item in data if item.get("id")]
        except Exception as e:
            logger.error(f"Erro ao listar modelos: {e}")
            return []

    @staticmethod
    def _extract_text_from_response(response: Dict) -> str:
        choices = response.get("choices", [])
        if not choices:
            return ""

        message = choices[0].get("message", {})
        content = message.get("content", "")
        return content.strip() if isinstance(content, str) else ""

    def _candidate_models(self) -> List[str]:
        candidates = [self.model]
        if NeuraConfig.LLM_MODEL_FALLBACK and NeuraConfig.LLM_MODEL_FALLBACK not in candidates:
            candidates.append(NeuraConfig.LLM_MODEL_FALLBACK)
        return candidates

    def _chat_completion(self, messages: List[Dict[str, str]], model: str) -> Dict:
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.3,
        }

        response = requests.post(
            self.chat_url,
            headers=self.headers,
            json=payload,
            timeout=NeuraConfig.REQUEST_TIMEOUT,
        )

        if response.status_code >= 400:
            detail = response.text[:300]
            raise RuntimeError(f"HTTP {response.status_code} ({model}): {detail}")

        return response.json()

    def get_response(
        self,
        user_msg: str,
        image_path: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """Gera resposta da IA, decidindo entre texto e visao."""
        try:
            if not NeuraConfig.GROQ_API_KEY:
                return "Erro: GROQ_API_KEY nao encontrado. Verifique o arquivo .env."

            if image_path and os.path.exists(image_path):
                logger.info(f"Iniciando modo visao para: {image_path}")
                print("Modo Visao ativado...")
                analise = self.vision.process_and_analyze(image_path, user_msg)

                if analise and self.use_memory:
                    self.save_message("assistant", f"[Visao]: {analise}")
                return analise

            if image_path and not os.path.exists(image_path):
                return f"Erro: arquivo de imagem nao encontrado em '{image_path}'."

            if history:
                contexto = [msg.copy() for msg in history]
                if self.system_prompt and (not contexto or contexto[0].get("role") != "system"):
                    contexto.insert(0, {"role": "system", "content": self.system_prompt})
                contexto.append({"role": "user", "content": user_msg})
            elif self.use_memory:
                self.save_message("user", user_msg)
                contexto = self.get_context()
            else:
                contexto = []
                if self.system_prompt:
                    contexto.append({"role": "system", "content": self.system_prompt})
                contexto.append({"role": "user", "content": user_msg})

            final_text = ""
            last_error = ""
            for model_name in self._candidate_models():
                try:
                    response = self._chat_completion(contexto, model_name)
                    final_text = self._extract_text_from_response(response)
                    if final_text:
                        break
                except Exception as e:
                    last_error = str(e)
                    logger.warning(f"Falha no modelo {model_name}: {e}")

            if final_text:
                if self.use_memory:
                    self.save_message("assistant", final_text)
                return final_text

            if last_error:
                return f"Erro na Groq API: {last_error}"

            return "Neura: Nao consegui gerar uma resposta no momento."
        except Exception as e:
            logger.error(f"Erro critico no Core: {e}", exc_info=True)
            return f"Erro no Core: {str(e)}"

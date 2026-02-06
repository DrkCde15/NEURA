import os
import base64
import requests
from io import BytesIO
from typing import Optional, Dict
from PIL import Image
from .config import NeuraConfig

class NeuraVision:
    def __init__(self, model: str = NeuraConfig.VISION_MODEL, 
                 host: str = NeuraConfig.OLLAMA_BASE_URL,
                 headers: Optional[Dict[str, str]] = None):
        self.model = model
        self.host = host
        self.headers = headers or {}
        self.url = f"{self.host}/api/generate"

    def process_and_analyze(self, image_path: str, prompt: str = "Describe this image objectively") -> str:
        """Redimensiona e envia para análise via API direta."""
        try:
            if not os.path.exists(image_path):
                return "Erro: Arquivo de imagem não encontrado."

            # 1. Redimensionamento Otimizado (Pillow)
            with Image.open(image_path) as img:
                img = img.convert("RGB")
                img.thumbnail(NeuraConfig.IMAGE_SIZE)
                buffered = BytesIO()
                img.save(buffered, format="JPEG", quality=NeuraConfig.IMAGE_QUALITY)
                img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

            # 2. Preparação do Payload
            payload = {
                "model": self.model,
                "prompt": prompt,
                "images": [img_base64],
                "stream": False,
                "options": {"temperature": 0}
            }

            # 3. Requisição Direta
            response = requests.post(
                self.url, 
                json=payload,
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                return response.json().get("response", "").strip()
            return f"Erro na API de Visão: {response.status_code}"

        except Exception as e:
            return f"Falha no módulo de imagem: {str(e)}"
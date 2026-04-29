import base64
import os
from io import BytesIO
from typing import Dict, Optional

import requests
from PIL import Image

from .config import NeuraConfig


class NeuraVision:
    def __init__(
        self,
        model: str = NeuraConfig.VISION_MODEL,
        api_base_url: str = NeuraConfig.GROQ_API_BASE_URL,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.model = model
        self.api_base_url = api_base_url.rstrip("/")
        self.url = f"{self.api_base_url}/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {NeuraConfig.GROQ_API_KEY}",
        }
        if headers:
            self.headers.update(headers)

    def process_and_analyze(
        self,
        image_path: str,
        prompt: str = "Describe this image objectively",
    ) -> str:
        """Redimensiona e envia para analise via Groq multimodal."""
        try:
            if not os.path.exists(image_path):
                return "Erro: arquivo de imagem nao encontrado."

            if not NeuraConfig.GROQ_API_KEY:
                return "Erro: GROQ_API_KEY nao encontrado. Verifique o arquivo .env."

            with Image.open(image_path) as img:
                img = img.convert("RGB")
                img.thumbnail(NeuraConfig.IMAGE_SIZE)
                buffered = BytesIO()
                img.save(buffered, format="JPEG", quality=NeuraConfig.IMAGE_QUALITY)
                img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{img_base64}"
                                },
                            },
                        ],
                    }
                ],
                "temperature": 0,
            }

            response = requests.post(
                self.url,
                json=payload,
                headers=self.headers,
                timeout=NeuraConfig.REQUEST_TIMEOUT,
            )

            if response.status_code >= 400:
                detail = response.text[:300].strip()
                return f"Erro na API de visao ({response.status_code}): {detail}"

            data = response.json()
            choices = data.get("choices", [])
            if not choices:
                return "Erro: resposta de visao sem conteudo."

            content = choices[0].get("message", {}).get("content", "")
            if isinstance(content, str):
                return content.strip()

            return "Erro: formato de resposta de visao nao suportado."
        except Exception as e:
            return f"Falha no modulo de imagem: {str(e)}"

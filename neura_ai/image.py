import os
import base64
import requests
from io import BytesIO
from PIL import Image

class NeuraVision:
    def __init__(self, model="moondream"):
        self.model = model
        self.url = "http://127.0.0.1:11434/api/generate"

    def process_and_analyze(self, image_path, prompt="Describe this image objectively"):
        """Redimensiona e envia para análise via API direta."""
        try:
            if not os.path.exists(image_path):
                return "Erro: Arquivo de imagem não encontrado."

            # 1. Redimensionamento Otimizado (Pillow)
            with Image.open(image_path) as img:
                img = img.convert("RGB")
                img.thumbnail((320, 320))
                buffered = BytesIO()
                img.save(buffered, format="JPEG", quality=80)
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
                timeout=120
            )

            if response.status_code == 200:
                return response.json().get("response", "").strip()
            return f"Erro na API de Visão: {response.status_code}"

        except Exception as e:
            return f"Falha no módulo de imagem: {str(e)}"
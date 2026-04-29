# NEURA AI - Inteligencia Artificial Multimodal

[![Versao](https://img.shields.io/badge/vers%C3%A3o-0.5.0-blue.svg)](https://github.com/DrkCde15/NEURA)
[![Python](https://img.shields.io/badge/python-3.9%2B-yellow.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

NEURA AI e um ecossistema modular em Python para conversa com LLM e analise de imagem, agora integrado com a **Groq API** (formato OpenAI-compatible).

## Estrutura

```text
NEURA/
|-- neura_ai/
|   |-- config.py
|   |-- core.py
|   |-- image.py
|   |-- __init__.py
|   `-- .env
|-- pyproject.toml
|-- requirements.txt
`-- README.md
```

## Funcionalidades

- Memoria persistente em SQLite.
- Chat com Groq via `/chat/completions`.
- Visao computacional com imagem local convertida para base64.
- Fallback de modelo (`GROQ_MODEL_FALLBACK`) quando configurado.
- Carregamento automatico de variaveis de ambiente (`.env`).

## Requisitos

- Python 3.9+
- Conta/chave Groq

## Instalacao

```bash
pip install -e .
```

## Configuracao (.env)

Voce pode usar `.env` na raiz do projeto ou em `neura_ai/.env`.

Exemplo:

```env
GROQ_API_KEY=seu_token_aqui
GROQ_MODEL=groq/compound
GROQ_MODEL_FALLBACK=groq/compound-mini
GROQ_VISION_MODEL=groq/compound
GROQ_API_BASE_URL=https://api.groq.com/openai/v1
GROQ_MODELS_URL=https://api.groq.com/openai/v1/models
NEURA_DB_PATH=data_memory.db
NEURA_REQUEST_TIMEOUT=30
```

Observacao:
- Se `GROQ_VISION_MODEL` nao for definido, a visao usa o mesmo valor de `GROQ_MODEL`.

## Uso basico

```python
from neura_ai.core import Neura

n = Neura(system_prompt="Voce e um assistente tecnico.")

if n.health_check():
    print(n.get_response("Como otimizar um loop em Python?"))
else:
    print("A API Groq nao esta acessivel.")
```

## Uso com imagem

```python
from neura_ai.core import Neura

n = Neura()
resposta = n.get_response("O que voce ve nesta imagem?", image_path="foto.jpg")
print(resposta)
```

## Metodos principais

- `health_check()`: verifica conectividade com Groq.
- `list_models()`: lista modelos disponiveis.
- `get_response(...)`: resposta textual ou visual.
- `clear_memory()`: limpa historico SQLite.

## Licenca

Distribuido sob a licenca MIT. Veja [LICENSE](LICENSE).

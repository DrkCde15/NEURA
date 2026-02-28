# NEURA AI 🤖 — Inteligência Artificial Multimodal Local

[![Versão](https://img.shields.io/badge/vers%C3%A3o-0.3.0-blue.svg)](https://github.com/DrkCde15/NEURA)
[![Python](https://img.shields.io/badge/python-3.8+-yellow.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**NEURA AI** é um ecossistema de inteligência artificial modular desenvolvido em Python, focado em **Multimodalidade Local**. Projetado para ser leve e resiliente, ele permite interações avançadas de texto e visão computacional, rodando inteiramente no seu hardware ou via túnel privado.

O diferencial da Neura é sua arquitetura desacoplada que utiliza **LLMs locais via Ollama**, uma **Memória Persistente Contextual (SQLite)** e um sistema de **Acesso Remoto Seguro** automatizado via LocalTunnel, garantindo que sua IA pessoal esteja disponível em qualquer lugar sem comprometer a privacidade.

---

## 📂 Estrutura do Projeto

```text
NEURA/
├── neura_ai/               # Core da biblioteca
│   ├── config.py           # Central de configurações (Modelos, URLs, DB)
│   ├── core.py             # Cérebro: Gestão de Memória SQL e Chat
│   ├── image.py            # Especialista em Visão Computacional (PIL/Base64)
│   └── __init__.py         # Inicialização do pacote (v0.3.0)
├── ecosystem.config.js     # Automação PM2 (Servidor Ollama + Túnel Local)
├── pyproject.toml          # Configuração de empacotamento PyPI/Pip
├── .gitignore              # Proteção de dados sensíveis e logs
├── requirements.txt        # Dependências (ollama, Pillow, requests)
└── README.md               # Você está aqui!
```

---

## ✨ Principais Funcionalidades

- **🧠 Memória Persistente:** Histórico de conversas automático via SQLite, permitindo que a IA se lembre de interações passadas.
- **👁️ Visão Computacional:** Processamento otimizado de imagens (redimensionamento para 320px) com o modelo `moondream`.
- **🌐 Acesso Remoto Inteligente:** Integração nativa com **LocalTunnel** com bypass automático de segurança (headers).
- **💓 Health Check Integrado:** Método para verificar se o servidor de IA está online antes de enviar requisições.
- **⚙️ Configuração Centralizada:** `config.py` permite trocar modelos (`qwen2`, `llama3`, etc) e parâmetros sem alterar o código principal.
- **🛡️ Resiliência Industrial:** Tratamento de erros para falhas de rede, rede indisponível e problemas de codificação.
- **⚡ Automação com PM2:** Gerenciamento de processos para manter o servidor e o túnel ativos 24/7.

---

## 🚀 Instalação e Configuração

### 1. Pré-requisitos

- [Ollama](https://ollama.com/) instalado.
- [Node.js](https://nodejs.org/) (para LocalTunnel e PM2).
- Python 3.8 ou superior.

### 2. Instalação Tradicional

```bash
# Clone o repositório ou baixe os arquivos
pip install -e .
```

### 3. Configuração do Servidor (Windows)

Para permitir acesso remoto via rede local ou túnel, configure as variáveis de ambiente:

```powershell
$env:OLLAMA_HOST="0.0.0.0"
$env:OLLAMA_ORIGINS="*"
```

### 4. Automação (PM2)

Mantenha sua IA sempre online com gerenciamento de processos:

```bash
npm install -g pm2 localtunnel
pm2 start ecosystem.config.js
pm2 save
```

---

## 🛠️ Exemplos de Uso

### Uso Local (com Histórico SQLite)

A Neura gerencia o contexto automaticamente para você.

```python
from neura_ai.core import Neura

# Inicializa com prompt de sistema personalizado
n = Neura(system_prompt="Você é um assistente técnico especializado em Python.")

# Verifica se o servidor está online
if n.health_check():
    print(n.get_response("Como posso otimizar um loop em Python?"))
else:
    print("O servidor Ollama não está acessível.")
```

### Inteligência Visual

A Neura processa a imagem localmente antes de enviar, economizando largura de banda:

```python
from neura_ai.core import Neura

n = Neura()
feedback = n.get_response("O que você vê nesta imagem?", image_path="foto.jpg")
print(f"Análise da IA: {feedback}")
```

### Modo Cloud Privada (Remote Access)

Se você configurou o túnel no `config.py`, pode acessar de qualquer lugar:

```python
from neura_ai.core import Neura
from neura_ai.config import NeuraConfig

# Conecta ao túnel fixo (ex: https://neura-ai.loca.lt)
n = Neura(host=NeuraConfig.TUNNEL_URL)
print(n.get_response("Estou te acessando remotamente?"))
```

---

## ⚙️ Configurações Disponíveis (`config.py`)

Você pode ajustar os seguintes parâmetros para melhor performance no seu hardware:

- `LLM_MODEL`: Modelo de linguagem (default: `qwen2:0.5b`).
- `VISION_MODEL`: Modelo de visão (default: `moondream`).
- `IMAGE_SIZE`: Tamanho máximo para redimensionamento (default: `320x320`).
- `DB_PATH`: Caminho do banco de dados SQLite.

---

## 📜 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

Desenvolvido com 🤖 por [DrkCde15](https://github.com/DrkCde15).

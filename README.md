# NEURA AI 🤖

## 1. Visão Geral

**NEURA AI** é um ecossistema de inteligência artificial modular desenvolvido em Python, focado em **Multimodalidade Local**. Projetado para ser leve e resiliente em hardware com recursos limitados (especialmente sistemas com 4GB de RAM), ele permite interações por texto, voz (STT/TTS) e **visão computacional**.

O diferencial da Neura é sua arquitetura desacoplada que utiliza **LLMs locais via Ollama**, uma **Memória Persistente Contextual (SQLite)** e um sistema de **Acesso Remoto Seguro** automatizado, garantindo que sua IA pessoal esteja disponível em qualquer lugar.

## 2. Árvore de Diretórios Atualizada

```text
NEURA/
├── neura_ai/               # Pacote principal da biblioteca
│   ├── audio.py            # Módulo de voz (STT/TTS)
│   ├── config.py           # NOVO: Central de configurações e URLs
│   ├── core.py             # Cérebro Multimodal e Gestão de Memória SQL
│   ├── image.py            # Especialista em Visão Computacional
│   └── __init__.py         # Exposição de classes e versão
├── test/                   # Scripts de exemplo e testes
│   ├── main.py             # Chat interativo principal
│   └── test_tunnel.py      # Teste de conectividade remota
├── pyproject.toml          # Configuração de empacotamento PyPI
├── .gitignore              # Proteção de bancos de dados e logs
└── requirements.txt        # Dependências do projeto
```

## 3. Principais Funcionalidades

- **🧠 Memória de Longo Prazo:** Utiliza SQLite para manter o contexto entre sessões.
- **👁️ Visão Adaptativa:** Redimensionamento inteligente de imagem (320px) para processamento instantâneo.
- **🌐 Acesso Remoto Nativo:** Suporte integrado a túneis (LocalTunnel) com bypass de segurança automático.
- **⚙️ Configuração Centralizada:** Gerencie modelos, caminhos e parâmetros em um único arquivo (`config.py`).
- **🛡️ Robustez Industrial:** Tratamento de erros para falhas de rede, problemas de encoding no Windows e health checks automáticos.
- **⚡ Automação com PM2:** Script de ecossistema para manter a IA e o Túnel online 24/7.

## 4. Instalação e Configuração

### Pré-requisitos

- [Ollama](https://ollama.com/) instalado.
- [Node.js](https://nodejs.org/) (para automação com PM2 e LocalTunnel).

```bash
# Instale a biblioteca
pip install neura_ai
```

### Configuração do Servidor (Windows)

Para permitir que o Neura AI seja acessado remotamente, configure as variáveis de ambiente do Ollama:

```powershell
$env:OLLAMA_HOST="0.0.0.0"
$env:OLLAMA_ORIGINS="*"
```

### Automação (PM2)

Mantenha sua IA sempre online com um único comando:

```bash
npm install -g pm2 pm2-windows-startup localtunnel
pm2 start ecosystem.config.js
pm2 save
```

## 5. Exemplo de Uso

### Uso Local

```python
from neura_ai.core import Neura

# Inicializa com padrões (qwen2:0.5b)
n = Neura(system_prompt="Você é um assistente prestativo.")
print(n.get_response("Olá, quem é você?"))
```

### Uso Remoto (Nuvem Privada)

Se você configurou o túnel, pode usar sua Neura de qualquer lugar do mundo:

```python
from neura_ai.core import Neura
from neura_ai.config import NeuraConfig

# Conecta ao seu link fixo automaticamente
n = Neura(host=NeuraConfig.TUNNEL_URL)
print(n.get_response("Diga 'Olá' pela internet!"))
```

## 6. Visão Computacional

A Neura processa imagens de forma ultra-rápida. No chat interativo (`test/main.py`), você pode enviar o caminho de uma imagem:

```text
Usuário: analise_imagem
Bot: Cole o caminho da imagem...
```

O sistema redimensiona a imagem, converte para Base64 e envia para o modelo `moondream` de forma otimizada.

---

Desenvolvido por DrkCde15.

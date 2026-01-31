# NEURA AI 🤖

## 1. Visão Geral

**NEURA AI** é um ecossistema de inteligência artificial modular desenvolvido em Python, focado em **Multimodalidade Local**. Projetado para ser leve e resiliente em hardware com recursos limitados (especialmente sistemas com 4GB de RAM), ele permite interações por texto, voz (STT/TTS) e **visão computacional**.

O diferencial da Neura é sua arquitetura desacoplada que utiliza **LLMs locais via Ollama**, uma **Memória Persistente Contextual (SQLite)** e um pipeline de processamento de imagem otimizado com **Pillow**, garantindo privacidade total e baixo consumo de memória.

## 2. Árvore de Diretórios Atualizada

```text
NEURA/
├── neura_ai/               # Pacote principal da biblioteca
│   ├── __init__.py         # Exposição de classes e versão
│   ├── audio.py            # Módulo de voz (STT/TTS)
│   ├── image.py            # NOVO: Especialista em Visão Computacional
│   └── core.py             # Cérebro Multimodal e Gestão de Memória SQL
├── test/                   # Scripts de exemplo e testes
│   ├── robot_test.py       # Chat Híbrido: Veterinária + Visão
│   ├── gato.jpeg           # Asset de teste de visão
│   └── cubo.jpg            # Asset de teste de visão
├── .gitignore              # Proteção de arquivos (.db, venv, imagens)
├── pyproject.toml          # Configuração de empacotamento
├── README.md               # Documentação do projeto
└── requirements.txt        # Lista de dependências (Pillow, requests, etc.)

```

## 3. Arquitetura de Componentes

* **`neura_ai/core.py` (Cérebro):** O ponto central que orquestra a memória SQL e a lógica de decisão entre texto e visão.
* **`neura_ai/image.py` (Olhos):** Módulo especializado que utiliza **Pillow** para redimensionar imagens para **320px** e gerencia a comunicação via API REST com o modelo de visão.
* **`neura_ai/audio.py` (Sintonia):** Interface de voz utilizando `SpeechRecognition` para entrada e `pyttsx3` para saída.
* **Gestão de Memória:** Banco de dados `data_memory.db` que armazena diálogos e descrições de imagens, permitindo que a IA "lembre" do que viu em conversas futuras.

## 4. Fluxo de Dados e Visão Otimizada

1. **Entrada:** Texto, voz ou **caminho de arquivo de imagem**.
2. **Pipeline de Visão:** O módulo `image.py` converte a imagem em um buffer Base64 ultraleve para evitar latência no barramento de dados.
3. **Processamento Multimodal:**
* **Visão:** Modelo `moondream` gera uma descrição técnica da imagem.
* **Texto:** Modelo `qwen2:0.5b` interpreta a análise e aplica a persona configurada (ex: Veterinária).


4. **Persistência:** Todo o ciclo é registrado no SQLite para garantir a continuidade do contexto.

## 5. Tecnologias e Dependências

* **IA Local:** [Ollama](https://ollama.com/).
* **Modelos Recomendados:** `qwen2:0.5b` (Linguagem) e `moondream` (Visão).
* **Processamento de Imagem:** `Pillow`.
* **Rede:** `requests` para chamadas de API estáveis.
* **Voz:** `pyttsx3` e `SpeechRecognition`.

## 6. Como Começar

### Pré-requisitos

* Ollama instalado e rodando.
* Modelos baixados:
```bash
ollama pull qwen2:0.5b
ollama pull moondream

```



### Instalação

```bash
# Clone o repositório
git clone https://github.com/DrkCde15/NEURA.git
cd NEURA

# Instale as dependências
pip install -r requirements.txt

```

### Executando o Chat

```bash
python test/robot_test.py

```

> **Dica:** No chat, você pode arrastar arquivos de imagem diretamente para o terminal para que a Neura realize a análise visual automática.

---
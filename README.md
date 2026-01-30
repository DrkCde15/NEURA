# NEURA AI 🤖

## 1. Visão Geral

**NEURA AI** é um ecossistema de inteligência artificial modular desenvolvido em Python. Projetado para ser leve e eficiente, ele permite interações por texto e voz (STT/TTS) utilizando Large Language Models (LLMs) locais via **Ollama**.

O diferencial da Neura é sua **Memória Persistente Contextual** baseada em SQLite, permitindo que a IA mantenha o histórico de diálogos mesmo após reiniciar o sistema, tudo rodando localmente para garantir total privacidade.

## 2. Árvore de Diretórios Atualizada

```text
NEURA/
├── neura_ai/               # Pacote principal da biblioteca
│   ├── __init__.py         # Exposição de classes e versão
│   ├── audio.py            # Módulo de voz (STT/TTS)
│   └── core.py             # Cérebro da IA e Gestão de Memória SQL
├── test/                   # Scripts de exemplo e testes
│   └── robot_test.py       # Exemplo: Agente Veterinário
├── .gitignore              # Proteção de arquivos sensíveis (.db, venv, dist)
├── pyproject.toml          # Configuração de empacotamento e dependências
├── README.md               # Documentação do projeto
└── requirements.txt        # Lista de dependências para pip

```

## 3. Arquitetura de Componentes

* **`neura_ai/core.py` (The Brain):** Gerencia a comunicação com o Ollama. Implementa travas de segurança (temperatura baixa) para evitar alucinações e gerencia o banco de dados `data_memory.db`.
* **`neura_ai/audio.py` (The Senses):** Interface de voz utilizando `SpeechRecognition` para entrada e `pyttsx3` para síntese de fala em português.
* **`pyproject.toml`:** Define os metadados do projeto e isola a biblioteca de scripts de teste, permitindo a instalação via `pip install .`.

## 4. Fluxo de Dados e Memória

1. **Entrada:** O usuário envia texto ou comando de voz.
2. **Recuperação:** A Neura busca as últimas 3 interações no **SQLite** para compor o contexto.
3. **Processamento:** O prompt é enviado ao Ollama com o modelo `qwen2:0.5b` (recomendado para < 4GB RAM).
4. **Persistência:** A resposta da IA é salva automaticamente no banco antes de ser exibida/falada.

## 5. Tecnologias e Dependências

* **IA Local:** [Ollama](https://ollama.com/) (Modelos recomendados: `qwen2:0.5b` ou `llama3.2:1b`).
* **Banco de Dados:** SQLite3 (Nativo do Python).
* **Voz:** `pyttsx3` e `SpeechRecognition`.
* **Interface:** `pyfiglet` para banners ASCII.

## 6. Como Começar

### Pré-requisitos

* Ollama instalado e rodando.
* Modelo baixado: `ollama pull qwen2:0.5b`

### Instalação

```bash
# Clone o repositório
git clone https://github.com/DrkCde15/NEURA.git
cd NEURA

# Instale as dependências
pip install -r requirements.txt

```

### Executando o Exemplo (Agente Veterinário)

```bash
python robot_test.py

```
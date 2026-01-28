# NEURA AI

## 1. Visão Geral

**Visão Geral:**
NEURA AI é um assistente de inteligência artificial interativo desenvolvido em Python. Ele foi projetado para se comunicar com o usuário tanto por entrada de texto quanto por voz, oferecendo uma experiência flexível. Utiliza um Large Language Model (LLM) via Ollama para processar e gerar respostas, enquanto gerencia a memória da conversa para manter o contexto ao longo da interação. A funcionalidade de voz é implementada através de reconhecimento de fala (STT) e síntese de fala (TTS), configurada para interações em português.

## 2. Árvore de Diretórios

```
NEURA/
├── main.py
├── requirements.txt
├── neura_ai/
    ├── audio.py
    ├── core.py
    └── __init__.py
```

## 3. Explicação do Papel de Cada Pasta Principal

*   **`NEURA/` (Diretório Raiz do Projeto):**
    Este é o diretório principal do projeto. Contém o ponto de entrada da aplicação (`main.py`), os requisitos de dependência (`requirements.txt`) e o pacote principal da aplicação (`neura_ai/`).

*   **`neura_ai/` (Pacote da Aplicação):**
    Este diretório constitui o pacote Python principal da NEURA AI. Ele encapsula a lógica central do assistente, modularizada em componentes como manipulação de áudio e a inteligência central.
    *   **`__init__.py`:** Marca `neura_ai` como um pacote Python. Ele também serve para expor as classes `Neura` e `NeuraVoice` diretamente do pacote (`from neura_ai import Neura`), simplificando as importações para o código cliente. Define a versão do pacote.
    *   **`audio.py`:** Contém a implementação da classe `NeuraVoice`, responsável por todas as funcionalidades de entrada e saída de áudio, incluindo reconhecimento de fala (Speech-to-Text - STT) e síntese de fala (Text-to-Speech - TTS).
    *   **`core.py`:** Contém a implementação da classe `Neura`, que representa o "cérebro" da IA. Esta classe lida com a interação com o Large Language Model (LLM), o gerenciamento da memória da conversa (persistência) e a lógica principal de processamento das requisições do usuário.

## 4. Fluxo de Dados

O fluxo de dados no projeto NEURA AI segue um padrão cliente-servidor/orquestrador, onde `main.py` atua como o orquestrador principal:

1.  **Inicialização (`main.py`):**
    *   A execução começa em `main.py`, que imprime um banner de boas-vindas.
    *   Instancia `Neura()` (o cérebro da IA) e `NeuraVoice()` (o módulo de áudio).
    *   `Neura` inicializa sua conexão com o banco de dados SQLite (`data_memory.db`) para gerenciar a memória da conversa e configura o modelo Ollama a ser usado.
    *   `NeuraVoice` inicializa o motor de TTS (`pyttsx3`) e configura as propriedades, como a voz em português.

2.  **Entrada do Usuário (`main.py` -> `NeuraVoice`):**
    *   O `main.py` entra em um loop contínuo aguardando a entrada do usuário.
    *   Se o usuário digitar "voz", o controle é passado para `NeuraVoice.listen()`.
        *   `NeuraVoice.listen()` utiliza `SpeechRecognition` para capturar áudio do microfone e convertê-lo em texto.
        *   O texto resultante é retornado para `main.py`.
    *   Se o usuário digitar texto diretamente, essa entrada é utilizada.

3.  **Processamento da IA (`main.py` -> `Neura`):**
    *   A entrada do usuário (seja texto digitado ou convertido de voz) é passada para o método de interação da instância `Neura` (método implícito que processaria a entrada).
    *   A instância `Neura` fará o seguinte:
        *   Registrará a entrada do usuário na memória (`sqlite3`).
        *   Construirá o prompt para o LLM, possivelmente incluindo o histórico da conversa recuperado do SQLite.
        *   Enviará o prompt ao LLM configurado via `ollama`.
        *   Receberá a resposta do LLM.
        *   Registrará a resposta do LLM na memória (`sqlite3`).

4.  **Saída da IA (`Neura` -> `main.py` -> `NeuraVoice`):**
    *   A resposta gerada pelo LLM é retornada da instância `Neura` para `main.py`.
    *   `main.py` exibe a resposta textual da IA no console.
    *   Opcionalmente (não explícito nos snippets, mas inferido por `NeuraVoice`), a resposta pode ser passada para `NeuraVoice.speak()` (um método hipotético) para sintetizar e reproduzir a fala para o usuário.

5.  **Ciclo Contínuo:**
    *   O loop continua, aguardando a próxima interação do usuário, até que ele decida sair.

## 5. Tecnologias Detectadas

*   **Linguagem de Programação:**
    *   **Python:** A linguagem principal de desenvolvimento do projeto.

*   **Inteligência Artificial & Processamento de Linguagem Natural (NLP):**
    *   **Ollama:** Utilizado para interagir com Large Language Models (LLMs) localmente (ex: `gemma:2b`), permitindo que a IA gere respostas inteligentes e contextuais.

*   **Armazenamento de Dados:**
    *   **SQLite:** Um sistema de gerenciamento de banco de dados relacional leve e embutido, utilizado para armazenar a memória da conversa (histórico de interações), garantindo que a IA possa manter o contexto.

*   **Processamento de Áudio e Voz:**
    *   **SpeechRecognition:** Biblioteca Python para realizar reconhecimento de fala, convertendo áudio (capturado via microfone) em texto.
    *   **pyttsx3:** Biblioteca Python para conversão de texto em fala (Text-to-Speech - TTS), permitindo que a IA "fale" suas respostas.
    *   **PyAudio:** Uma dependência comum para bibliotecas de áudio em Python (como `SpeechRecognition` e `pyttsx3`) para acessar e controlar dispositivos de entrada/saída de áudio.

*   **Interface e Utilidades:**
    *   **pyfiglet:** Utilizado para gerar texto ASCII art, especificamente para o banner "NEURA AI" na inicialização da aplicação, tornando a interface inicial mais visualmente atraente.
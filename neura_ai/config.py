import os
from pathlib import Path

from dotenv import load_dotenv


def _load_env_files() -> None:
    current_dir = Path(__file__).resolve().parent
    root_dir = current_dir.parent

    candidates = [
        root_dir / ".env",
        current_dir / ".env",
    ]

    for env_path in candidates:
        if env_path.exists():
            load_dotenv(env_path, override=False)


_load_env_files()


class NeuraConfig:
    """Centralized configuration for NEURA AI."""

    REQUEST_TIMEOUT = int(os.getenv("NEURA_REQUEST_TIMEOUT", "30"))

    # Groq Settings
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_API_BASE_URL = os.getenv("GROQ_API_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/")
    GROQ_CHAT_URL = os.getenv(
        "GROQ_CHAT_URL",
        f"{GROQ_API_BASE_URL}/chat/completions",
    )
    GROQ_MODELS_URL = os.getenv(
        "BASE_URL",
        os.getenv("GROQ_MODELS_URL", f"{GROQ_API_BASE_URL}/models"),
    )

    LLM_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    LLM_MODEL_FALLBACK = os.getenv("GROQ_MODEL_FALLBACK", "")
    VISION_MODEL = os.getenv("GROQ_VISION_MODEL", LLM_MODEL)

    # Database Settings
    DB_PATH = os.getenv("NEURA_DB_PATH", "data_memory.db")

    # Vision Settings
    IMAGE_SIZE = (320, 320)
    IMAGE_QUALITY = 80

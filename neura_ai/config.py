class NeuraConfig:
    """Centralized configuration for NEURA AI."""
    
    # LLM Settings
    LLM_MODEL = "qwen2:0.5b"
    VISION_MODEL = "moondream"
    OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"
    OLLAMA_BASE_URL = "http://127.0.0.1:11434"

    # Database Settings
    DB_PATH = "data_memory.db"

    # Remote Tunnel (Optional)
    TUNNEL_URL = "https://neura-ai.loca.lt"
    BYPASS_HEADERS = {"Bypass-Tunnel-Reminder": "true"}
    
    # Vision Settings
    IMAGE_SIZE = (320, 320)
    IMAGE_QUALITY = 80

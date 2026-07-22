"""
NEXUS-OSINT: Centralized Configuration
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "NEXUS-OSINT"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Memgraph
    MEMGRAPH_HOST: str = "localhost"
    MEMGRAPH_PORT: int = 7687
    MEMGRAPH_USER: str = ""
    MEMGRAPH_PASSWORD: str = ""

    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Qdrant
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "nexus_entities"

    # External APIs
    VIRUSTOTAL_API_KEY: str = ""

    # LLM
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "http://localhost:11434/v1"
    LLM_MODEL: str = "qwen2.5:72b"

    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()

"""Centralized configuration."""
from functools import lru_cache
from pydantic_settings import BaseSettings,SettingsConfigDict
class Settings(BaseSettings):
 APP_NAME:str="NEXUS-OSINT"; APP_VERSION:str="2.0.0"; DEBUG:bool=False
 MEMGRAPH_HOST:str="localhost"; MEMGRAPH_PORT:int=7687; MEMGRAPH_USER:str=""; MEMGRAPH_PASSWORD:str=""
 REDIS_URL:str="redis://localhost:6379/0"; CELERY_BROKER_URL:str="redis://localhost:6379/1"; CELERY_RESULT_BACKEND:str="redis://localhost:6379/2"; NEXUS_USE_CELERY:bool=False
 QDRANT_HOST:str="localhost"; QDRANT_PORT:int=6333; QDRANT_COLLECTION:str="nexus_entities"
 VIRUSTOTAL_API_KEY:str=""; LLM_API_KEY:str=""; LLM_BASE_URL:str="http://localhost:11434/v1"; LLM_MODEL:str="qwen2.5:72b"; WS_HEARTBEAT_INTERVAL:int=30
 NEXUS_JWT_SECRET:str="change-me-in-production"; NEXUS_SESSION_MINUTES:int=480; NEXUS_CORS_ORIGINS:str="http://localhost:3000"
 model_config=SettingsConfigDict(env_file=".env",case_sensitive=True)
@lru_cache
def get_settings()->Settings:return Settings()

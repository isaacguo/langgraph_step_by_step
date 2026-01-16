import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "LangGraph Safety System"
    DEBUG: bool = False
    
    # LLM Configuration (LM Studio)
    LM_STUDIO_BASE_URL: str = "http://host.docker.internal:1234/v1"
    LM_STUDIO_MODEL: str = "qwen/qwen3-4b-2507"
    LM_STUDIO_API_KEY: str = "lm-studio"

    # Database Configuration
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/langgraph_db"
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"

    # Safety Configuration
    SAFETY_THRESHOLD: float = 0.8
    ENABLE_GUARDRAILS: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()

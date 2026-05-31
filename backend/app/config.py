from pydantic import field_validator
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Configuration
    API_TITLE: str = "AI Interview Simulator API"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "mongodb://localhost:27017/ai_interview"
    
    # JWT
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]
    
    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    # Development toggle: when true, avoid calling external LLMs and use deterministic defaults
    LLM_USE_MOCK: bool = False
    
    # Speech-to-Text
    ASSEMBLYAI_API_KEY: Optional[str] = None
    
    # Application
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, value):
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "production", "prod"}:
                return False
            if normalized in {"debug", "development", "dev"}:
                return True
        return value
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

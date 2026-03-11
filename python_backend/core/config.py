"""
Application configuration
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Schedulo"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5000",
        "http://localhost:5173",
        "http://127.0.0.1:5000",
        "http://127.0.0.1:5173",
    ]
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/schedulo"
    DEBUG: bool = False
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_MAX_TOKENS: int = 1000
    
    # Agent Settings
    AGENT_TIMEOUT: int = 30  # seconds
    LOOKBACK_DAYS: int = 90  # days of history to analyze
    CONFIDENCE_THRESHOLD: float = 0.6  # Escalate below this
    MAX_NEGOTIATION_ROUNDS: int = 3
    
    # Calendar Integration
    GOOGLE_CALENDAR_ENABLED: bool = False
    OUTLOOK_CALENDAR_ENABLED: bool = False
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/google/callback"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

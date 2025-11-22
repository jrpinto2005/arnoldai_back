from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./arnold.db"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # AI Services
    openai_api_key: Optional[str] = None
    elevenlabs_api_key: Optional[str] = None
    
    # App settings
    app_name: str = "Arnold Fitness Coach"
    debug: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()

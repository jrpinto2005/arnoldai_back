from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Arnold Coach API"
    DATABASE_URL: str = "sqlite:///./arnold.db"

    # LLM / IA
    LLM_API_KEY: str | None = None
    LLM_MODEL: str = "gpt-4.1-mini"  # o lo que vayan a usar

    # ElevenLabs
    ELEVENLABS_API_KEY: str | None = None
    ELEVENLABS_VOICE_ID: str | None = None

    class Config:
        env_file = ".env"


settings = Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 👇 Esto hace que Pydantic ignore variables que no estén declaradas
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    PROJECT_NAME: str = "Arnold Coach API"
    DATABASE_URL: str = "sqlite:///./arnold.db"

    # LLM / IA
    LLM_API_KEY: str | None = None
    LLM_MODEL: str = "gpt-4.1-mini"

    # ElevenLabs
    ELEVENLABS_API_KEY: str | None = None
    ELEVENLABS_VOICE_ID: str | None = None

    # Media
    MEDIA_DIR: str = "./media"


settings = Settings()

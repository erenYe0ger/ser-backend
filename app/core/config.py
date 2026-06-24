from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # PostgreSQL database connection URL
    DATABASE_URL: str

    # Redis connection URL for caching and background tasks
    REDIS_URL: str

    # Hugging Face Spaces endpoint URL
    HF_SPACES_URL: str

    # JWT signing secret
    JWT_SECRET_KEY: str

    # Google OAuth client ID
    GOOGLE_CLIENT_ID: str

    # Application name
    APP_NAME: str = "SER Backend"

    # Enable or disable debug mode
    DEBUG: bool = False

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
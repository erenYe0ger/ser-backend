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

    # Cloudflare R2 account ID
    R2_ACCOUNT_ID: str

    # Cloudflare R2 access key ID
    R2_ACCESS_KEY_ID: str

    # Cloudflare R2 secret access key
    R2_SECRET_ACCESS_KEY: str

    # Cloudflare R2 bucket name
    R2_BUCKET_NAME: str

    # Application name
    APP_NAME: str = "SER Backend"

    # Enable or disable debug mode
    DEBUG: bool = False

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
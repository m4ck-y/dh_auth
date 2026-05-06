"""Application settings loaded from environment variables via pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Configuration for the dh_auth microservice.

    Loads values from .env file with support for secrets, database connection,
    JWT configuration, and inter-service URLs.
    """

    PROJECT_NAME: str = "Digital Hospital - Auth Service"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    # Root path when running standalone (behind gateway path is controlled by gateway)
    ROOT_PATH: str = "/api/auth"
    CORS_ORIGINS: list[str] = ["*"]

    # PostgreSQL
    POSTGRES_URL: str = "postgresql+asyncpg://user:password@localhost:5432/dh_hospital"

    # Seguridad / JWT
    JWT_SECRET_KEY: str = "tu-llave-secreta-aqui"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Service URLs
    SERVICE_CORE_URL: str = ""
    SERVICE_IAM_URL: str = ""
    SERVICE_LOGGER_TRACER_URL: str = ""
    SERVICE_MESSAGE_SENDER_URL: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

settings = Settings()

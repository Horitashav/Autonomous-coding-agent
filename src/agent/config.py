from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Environment
    ENVIRONMENT: str = Field(default="production")
    DEBUG: bool = Field(default=False)
    PORT: int = Field(default=8000)
    ALLOWED_ORIGINS: list[str] = Field(
        default=["https://yourdomain.com"],
        description="Allowed CORS origins"
    )

    # Core Secrets - NO insecure fallbacks allowed in production
    JWT_SECRET_KEY: str = Field(..., min_length=32)
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440)

    DATABASE_URL: str = Field(..., description="PostgreSQL connection string")
    
    # LLM & Observability
    GROQ_API_KEY: str = Field(...)
    OPENAI_API_KEY: str | None = Field(default=None)
    LANGCHAIN_TRACING_V2: bool = Field(default=False)
    LANGCHAIN_API_KEY: str | None = Field(default=None)

    # Execution Bounds & Circuit Breakers
    MAX_RUN_BUDGET_USD: float = Field(default=0.50)
    MAX_RUN_TOKENS: int = Field(default=50_000)
    SANDBOX_TIMEOUT_SECONDS: int = Field(default=15)
    DOCKER_ENABLED: bool = Field(default=True)


settings = AppSettings()
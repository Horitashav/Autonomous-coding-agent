from pydantic import Field
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
        default=["https://yourdomain.com"], description="Allowed CORS origins"
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
    MAX_REPAIR_ATTEMPTS: int = Field(default=3)
    MAX_CODE_LENGTH: int = Field(default=10_000)
    LLM_MODEL: str = Field(default="openai/gpt-oss-120b")
    LLM_TEMPERATURE: float = Field(default=0.0)
    SANDBOX_TIMEOUT_SECONDS: int = Field(default=15)
    SANDBOX_MEMORY_LIMIT: str = Field(default="512m")
    SANDBOX_CPU_COUNT: int = Field(default=1)
    SANDBOX_PID_LIMIT: int = Field(default=64)
    SANDBOX_TMPFS_SIZE: str = Field(default="64m")
    SANDBOX_DOCKER_IMAGE: str = Field(default="agent-sandbox")
    DOCKER_ENABLED: bool = Field(default=True)
    FORBIDDEN_MODULES: set[str] = Field(
        default_factory=lambda: {
            "os",
            "subprocess",
            "shutil",
            "signal",
            "ctypes",
            "multiprocessing",
            "pty",
            "socket",
            "requests",
            "http",
            "urllib",
            "ftplib",
            "smtplib",
            "telnetlib",
            "xmlrpc",
            "webbrowser",
            "antigravity",
            "code",
            "codeop",
            "compileall",
            "importlib",
            "runpy",
            "pickle",
        }
    )


settings = AppSettings()

# Backward-compatible exports for modules that still import settings directly.
SANDBOX_DOCKER_IMAGE = settings.SANDBOX_DOCKER_IMAGE
SANDBOX_TIMEOUT_SECONDS = settings.SANDBOX_TIMEOUT_SECONDS
SANDBOX_MEMORY_LIMIT = settings.SANDBOX_MEMORY_LIMIT
SANDBOX_CPU_COUNT = settings.SANDBOX_CPU_COUNT
SANDBOX_PID_LIMIT = settings.SANDBOX_PID_LIMIT
SANDBOX_TMPFS_SIZE = settings.SANDBOX_TMPFS_SIZE
MAX_REPAIR_ATTEMPTS = settings.MAX_REPAIR_ATTEMPTS
MAX_CODE_LENGTH = settings.MAX_CODE_LENGTH
LLM_MODEL = settings.LLM_MODEL
LLM_TEMPERATURE = settings.LLM_TEMPERATURE
GROQ_API_KEY = settings.GROQ_API_KEY
FORBIDDEN_MODULES = settings.FORBIDDEN_MODULES
DATABASE_URL = settings.DATABASE_URL
JWT_SECRET_KEY = settings.JWT_SECRET_KEY
JWT_ALGORITHM = settings.JWT_ALGORITHM

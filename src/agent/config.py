from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Environment
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=False)
    PORT: int = Field(default=8000)
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
    )

    # Database
    POSTGRES_USER: str = Field(default="agent_admin")
    POSTGRES_PASSWORD: str = Field(default="agent_secret_password")
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)
    POSTGRES_DB: str = Field(default="agent_production_db")
    DATABASE_URL: str | None = Field(default=None)

    # Core Secrets
    JWT_SECRET_KEY: str = Field(..., min_length=32)
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440)

    # LLM Settings & Keys
    OPENAI_API_KEY: str = Field(default="")
    GROQ_API_KEY: str = Field(default="")
    LLM_MODEL: str = Field(default="gpt-4o-mini")
    LLM_TEMPERATURE: float = Field(default=0.0)
    MAX_CODE_LENGTH: int = Field(default=10_000)

    # Observability
    LANGCHAIN_TRACING_V2: bool = Field(default=False)
    LANGCHAIN_API_KEY: str = Field(default="")
    LANGCHAIN_PROJECT: str = Field(default="autonomous-coding-agent-studio")

    # Sandbox Hardware & Resource Constraints
    SANDBOX_DOCKER_IMAGE: str = Field(default="agent-sandbox")
    SANDBOX_MEMORY_LIMIT: str = Field(default="512m")
    SANDBOX_CPU_COUNT: int = Field(default=1)
    SANDBOX_TIMEOUT_SECONDS: int = Field(default=15)
    SANDBOX_PID_LIMIT: int = Field(default=64)
    SANDBOX_TMPFS_SIZE: str = Field(default="64m")
    DOCKER_ENABLED: bool = Field(default=True)

    # Agent Lifecycle
    MAX_REPAIR_ATTEMPTS: int = Field(default=3)
    MAX_RUN_BUDGET_USD: float = Field(default=0.50)
    MAX_RUN_TOKENS: int = Field(default=50_000)

    # Security Blocklist
    FORBIDDEN_MODULES: set[str] = {
        "os", "subprocess", "shutil", "signal", "ctypes", "multiprocessing",
        "pty", "socket", "requests", "http", "urllib", "ftplib", "smtplib",
        "telnetlib", "xmlrpc", "webbrowser", "pickle", "importlib", "runpy",
        "antigravity", "code", "codeop", "compileall",
    }

    @model_validator(mode="after")
    def assemble_database_url(self) -> "AppSettings":
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        return self

    @property
    def cors_origins(self) -> list[str]:
        if not self.ALLOWED_ORIGINS:
            return []
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


# Global instantiated settings
# Global instantiated settings
settings = AppSettings()

# Top-level backwards compatibility exports
ENVIRONMENT = settings.ENVIRONMENT
DEBUG = settings.DEBUG
PORT = settings.PORT
ALLOWED_ORIGINS = settings.cors_origins

POSTGRES_USER = settings.POSTGRES_USER
POSTGRES_PASSWORD = settings.POSTGRES_PASSWORD
POSTGRES_HOST = settings.POSTGRES_HOST
POSTGRES_PORT = settings.POSTGRES_PORT
POSTGRES_DB = settings.POSTGRES_DB
DATABASE_URL = settings.DATABASE_URL

JWT_SECRET_KEY = settings.JWT_SECRET_KEY
JWT_ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

OPENAI_API_KEY = settings.OPENAI_API_KEY
GROQ_API_KEY = settings.GROQ_API_KEY
LLM_MODEL = settings.LLM_MODEL
LLM_TEMPERATURE = settings.LLM_TEMPERATURE
MAX_CODE_LENGTH = settings.MAX_CODE_LENGTH

SANDBOX_DOCKER_IMAGE = settings.SANDBOX_DOCKER_IMAGE
SANDBOX_MEMORY_LIMIT = settings.SANDBOX_MEMORY_LIMIT
SANDBOX_CPU_COUNT = settings.SANDBOX_CPU_COUNT
SANDBOX_TIMEOUT_SECONDS = settings.SANDBOX_TIMEOUT_SECONDS
SANDBOX_PID_LIMIT = settings.SANDBOX_PID_LIMIT
SANDBOX_TMPFS_SIZE = settings.SANDBOX_TMPFS_SIZE
DOCKER_ENABLED = settings.DOCKER_ENABLED

MAX_REPAIR_ATTEMPTS = settings.MAX_REPAIR_ATTEMPTS
MAX_RUN_BUDGET_USD = settings.MAX_RUN_BUDGET_USD
MAX_RUN_TOKENS = settings.MAX_RUN_TOKENS
FORBIDDEN_MODULES = settings.FORBIDDEN_MODULES
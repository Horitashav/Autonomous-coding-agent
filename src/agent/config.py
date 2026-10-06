"""Central configuration for the Autonomous Coding Agent."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env file into os.environ
load_dotenv()

# ===========================================================================
# API KEYS
# ===========================================================================
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")


# ===========================================================================
# SANDBOX RESOURCE LIMITS
# ===========================================================================
SANDBOX_MEMORY_LIMIT: str = "512m"
SANDBOX_CPU_COUNT: int = 1
SANDBOX_TIMEOUT_SECONDS: int = 15
SANDBOX_PID_LIMIT: int = 64
SANDBOX_TMPFS_SIZE: str = "64m"
SANDBOX_DOCKER_IMAGE: str = "python:3.11-slim"

# ===========================================================================
# AGENT BEHAVIOR
# ===========================================================================
MAX_REPAIR_ATTEMPTS: int = 3
MAX_CODE_LENGTH: int = 10_000
LLM_MODEL: str = "openai/gpt-oss-120b"
LLM_TEMPERATURE: float = 0.0

# ===========================================================================
# SECURITY — FORBIDDEN MODULES
# ===========================================================================
FORBIDDEN_MODULES: set[str] = {
    # Operating System Access
    "os",
    "subprocess",
    "shutil",
    "signal",
    "ctypes",
    "multiprocessing",
    "pty",
    # Network Access
    "socket",
    "requests",
    "http",
    "urllib",
    "ftplib",
    "smtplib",
    "telnetlib",
    "xmlrpc",
    "webbrowser",
    # Dynamic Code Execution & Dangerous Utils
    "antigravity",
    "code",
    "codeop",
    "compileall",
    "importlib",
    "runpy",
    "pickle",
}

# ===========================================================================
# PATHS
# ===========================================================================
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent.parent

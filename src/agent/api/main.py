"""FastAPI Application Gateway — REST API server with health probes and dynamic CORS."""

import logging
import os
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from agent.api.database import engine
from agent.api.routes import agent, auth, chat

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Autonomous Coding Agent API",
    description="Production REST API backend with PostgreSQL, JWT Auth, and Docker Sandbox",
    version="1.0.0",
)

# Parse allowed origins dynamically from environment with local dev fallbacks
raw_origins = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
)
allowed_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(agent.router)


@app.get("/api/health")
@app.get("/health/live")
def liveness():
    """Liveness probe: verifies process is alive."""
    return {"status": "healthy", "service": "agent-api", "version": "1.0.0"}


@app.get("/health/ready")
def readiness(response: Response):
    """Readiness probe: validates database connectivity and Docker availability."""
    checks = {"database": False, "docker": False}

    # Verify PostgreSQL
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception as exc:
        logger.error(f"Readiness check: PostgreSQL ping failed: {exc}")

    # Verify Docker Daemon (non-fatal if offline)
    try:
        import docker

        client = docker.from_env()
        client.ping()
        checks["docker"] = True
    except Exception as exc:
        logger.warning(f"Readiness check: Docker ping failed: {exc}")

    if not checks["database"]:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unhealthy", "checks": checks}

    return {
        "status": "ready" if checks["docker"] else "degraded",
        "checks": checks,
    }

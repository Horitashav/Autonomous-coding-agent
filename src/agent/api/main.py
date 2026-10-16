"""FastAPI Application Gateway — Configured via centralized settings."""

import logging
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from agent.api.database import engine
from agent.api.routes import agent, auth, chat
from agent.config import settings

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Autonomous Coding Agent API",
    description="Production REST API backend with PostgreSQL, JWT Auth, and Docker Sandbox",
    version="1.0.0",
    debug=settings.DEBUG,
)

# Apply CORS origins validated by config.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(agent.router)


@app.get("/api/health")
@app.get("/health/live")
def liveness():
    return {"status": "healthy", "service": "agent-api", "version": "1.0.0"}


@app.get("/api/health/ready")
@app.get("/health/ready")
def readiness(response: Response):
    checks = {"database": False, "docker": False}

    # Verify Database connectivity
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception as exc:
        logger.error(f"Readiness check: DB ping failed: {exc}")

    # Verify Docker Daemon
    if settings.DOCKER_ENABLED:
        try:
            import docker
            client = docker.from_env()
            client.ping()
            checks["docker"] = True
        except Exception as exc:
            logger.error(f"Readiness check: Docker ping failed: {exc}")
    else:
        checks["docker"] = True

    # Fail-fast: Service is NOT ready if either critical dependency is failing
    if not checks["database"] or not checks["docker"]:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unhealthy", "checks": checks}

    return {"status": "ready", "checks": checks}
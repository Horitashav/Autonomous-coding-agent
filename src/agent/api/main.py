"""FastAPI Application Gateway — REST API server."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agent.api.routes import agent, auth, chat

app = FastAPI(
    title="Autonomous Coding Agent API",
    description="Production REST API backend with PostgreSQL, JWT Auth, and Docker Sandbox",
    version="1.0.0",
)

# CORS setup for frontend dashboard integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(agent.router)


@app.get("/api/health")
def health_check():
    """Health check endpoint for Docker and monitoring probes."""
    return {"status": "healthy", "database": "postgresql", "version": "1.0.0"}
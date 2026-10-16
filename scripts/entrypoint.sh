#!/bin/sh
set -e

echo "[STARTUP] Running database schema migration (alembic upgrade head)..."
alembic upgrade head

echo "[STARTUP] Database migrations applied successfully."
echo "[STARTUP] Launching Uvicorn production server..."
exec uvicorn agent.api.main:app --host 0.0.0.0 --port 8000 --workers 2
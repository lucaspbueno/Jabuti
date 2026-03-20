#!/bin/sh
set -e
cd /app
poetry run alembic upgrade head
exec poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir /app

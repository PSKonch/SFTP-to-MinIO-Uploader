#!/bin/sh
set -e

echo "Sleeping to wait for PostgreSQL..."
sleep 10

alembic upgrade head

exec uvicorn src.main:app --host 0.0.0.0 --port 8000
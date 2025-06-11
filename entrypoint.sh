#!/bin/sh

# Wait for PostgreSQL to be ready
until pg_isready -h postgres -U user; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

# Run database migrations
alembic upgrade head

# Start the application
uvicorn src.main:app --host 0.0.0.0 --port 8000
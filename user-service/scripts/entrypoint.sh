#!/bin/sh
set -e

# Run migrations
echo "Running Alembic migrations..."
alembic upgrade head

# Start the app
echo "Starting FastAPI app..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8001

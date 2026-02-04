#!/bin/sh
PORT="${PORT:-8000}"
echo "Waiting 5 seconds for dependencies..."
sleep 5
echo "Starting server on port $PORT"
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"

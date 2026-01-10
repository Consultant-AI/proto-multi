#!/bin/bash

# Start Proto - Backend + Electron Frontend
# This script stops any existing processes and starts fresh

cd "$(dirname "$0")"

echo "================================================"
echo "  Proto - Real Browser Edition"
echo "================================================"
echo ""

# Kill existing processes
echo "Stopping existing processes..."

# Kill backend on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "  Killed backend (port 8000)" || echo "  No backend running"

# Kill Electron processes (but not VS Code)
pkill -f "Electron.*webui-react" 2>/dev/null && echo "  Killed Electron frontend" || echo "  No Electron running"

# Kill Qt browser
pkill -f "qt_browser.py" 2>/dev/null && echo "  Killed Qt browser" || echo "  No Qt browser running"

# Kill any vite dev server on port 3000
lsof -ti:3000 | xargs kill -9 2>/dev/null && echo "  Killed Vite (port 3000)" || echo "  No Vite running"

sleep 1
echo ""

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ] && [ ! -f ~/.anthropic/api_key ]; then
    echo "Warning: No Anthropic API key found!"
    echo "   Set ANTHROPIC_API_KEY or create ~/.anthropic/api_key"
    echo ""
fi

# Load Hetzner API token from .env file if present
if [ -f "hetzner-deploy/.env" ]; then
    source hetzner-deploy/.env
    echo "Loaded Hetzner API token"
fi

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "Activated Python virtual environment"
else
    echo "Warning: No .venv found, using system Python"
fi

echo ""
echo "Starting services..."
echo ""

# Disable Qt browser - we're using Electron
export NO_QT_BROWSER=1

# Disable auto-open Chrome window - Electron is our frontend
export WEBUI_AUTO_OPEN=0

# Start backend in background
echo "Starting backend on http://localhost:8000..."
python3 -m computer_use_demo.webui &
BACKEND_PID=$!

# Wait for backend to be ready
echo "Waiting for backend..."
for i in {1..30}; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo "Backend ready!"
        break
    fi
    sleep 0.5
done

# Start Electron frontend
echo ""
echo "Starting Electron frontend..."
cd webui-react
unset ELECTRON_RUN_AS_NODE
npm run electron:dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "================================================"
echo "  Proto is running!"
echo ""
echo "  Backend:  http://localhost:8000"
echo "  Frontend: Electron app (opening...)"
echo ""
echo "  Press Ctrl+C to stop all services"
echo "================================================"
echo ""

# Handle Ctrl+C to kill both processes
cleanup() {
    echo ""
    echo "Stopping..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    pkill -f "Electron.*webui-react" 2>/dev/null
    lsof -ti:3000 | xargs kill -9 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for processes
wait

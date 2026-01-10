#!/bin/bash

# Stop all Proto services

echo "Stopping Proto services..."

# Kill backend on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "  Stopped backend (port 8000)" || echo "  No backend running"

# Kill Electron processes (but not VS Code)
pkill -f "Electron.*webui-react" 2>/dev/null && echo "  Stopped Electron frontend" || echo "  No Electron running"

# Kill Qt browser
pkill -f "qt_browser.py" 2>/dev/null && echo "  Stopped Qt browser" || echo "  No Qt browser running"

# Kill vite dev server on port 3000
lsof -ti:3000 | xargs kill -9 2>/dev/null && echo "  Stopped Vite (port 3000)" || echo "  No Vite running"

echo ""
echo "All services stopped."

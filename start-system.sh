#!/bin/bash
# Script to start both backend and frontend with correct configuration

echo "Starting Proto Multi System..."
echo "=============================="

# Use proto_coding_v1 with UniversalComputerTool (auto-detects environment)
export COMPUTER_USE_TOOL_VERSION=proto_coding_v1

# Start backend
echo "Starting backend on port 8000..."
cd /home/computeruse/proto-multi/computer-use-demo
PYTHONUNBUFFERED=1 python -m computer_use_demo.webui > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID)"

# Wait for backend to start
sleep 5

# Start frontend
echo "Starting frontend on port 3000..."
cd /home/computeruse/proto-multi/computer-use-demo/webui-react
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend started (PID: $FRONTEND_PID)"

echo ""
echo "System ready!"
echo "================================"
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Backend logs: tail -f /tmp/backend.log"
echo "Frontend logs: tail -f /tmp/frontend.log"
echo ""
echo "To stop: kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "PIDs saved to /tmp/proto_pids.txt"
echo "$BACKEND_PID $FRONTEND_PID" > /tmp/proto_pids.txt

#!/bin/bash
# Auto-start VNC server for remote desktop viewing

echo "🖥️  Starting VNC server..."

# Detect platform
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "Detected macOS"

    # Check if x11vnc is installed
    if ! command -v x11vnc &> /dev/null; then
        echo "⚠️  x11vnc not installed. Install with: brew install x11vnc"
        exit 1
    fi

    # Start x11vnc on display :0 (main display)
    x11vnc -display :0 -forever -shared -rfbport 5900 -nopw &
    X11VNC_PID=$!
    echo "✓ x11vnc started (PID: $X11VNC_PID)"

elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux (Ubuntu)
    echo "Detected Linux"

    # Check if x11vnc is installed
    if ! command -v x11vnc &> /dev/null; then
        echo "⚠️  x11vnc not installed. Install with: sudo apt-get install x11vnc"
        exit 1
    fi

    # Start x11vnc on display :0
    x11vnc -display :0 -forever -shared -rfbport 5900 -nopw &
    X11VNC_PID=$!
    echo "✓ x11vnc started (PID: $X11VNC_PID)"
fi

# Wait for x11vnc to start
sleep 2

# Start noVNC proxy
echo "🌐 Starting noVNC proxy..."

# Check if noVNC is available locally
if [ -f "node_modules/.bin/novnc" ]; then
    # Use local noVNC installation
    npx novnc --vnc localhost:5900 --listen 6080 &
    NOVNC_PID=$!
    echo "✓ noVNC started on port 6080 (PID: $NOVNC_PID)"
elif command -v novnc &> /dev/null; then
    # Use globally installed noVNC
    novnc --vnc localhost:5900 --listen 6080 &
    NOVNC_PID=$!
    echo "✓ noVNC started on port 6080 (PID: $NOVNC_PID)"
else
    echo "⚠️  noVNC not found. Install with: npm install novnc"
fi

echo ""
echo "✅ VNC server ready!"
echo "   - VNC: localhost:5900"
echo "   - noVNC: http://localhost:6080"

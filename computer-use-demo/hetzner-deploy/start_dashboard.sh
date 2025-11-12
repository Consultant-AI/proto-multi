#!/bin/bash
# Start the Hetzner Control Panel Dashboard

cd "$(dirname "$0")"

# Load environment variables
if [ -f .env ]; then
    source .env
else
    echo "Error: .env file not found"
    exit 1
fi

# Check required variables
if [ -z "$HETZNER_API_TOKEN" ]; then
    echo "Error: HETZNER_API_TOKEN not set in .env"
    exit 1
fi

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Error: ANTHROPIC_API_KEY not set in .env"
    exit 1
fi

echo "Starting Hetzner Control Panel..."
echo "HETZNER_API_TOKEN: ${HETZNER_API_TOKEN:0:20}..."
echo "ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:0:20}..."

# Kill any existing dashboard process
lsof -ti:5500 | xargs kill -9 2>/dev/null || true

# Start the dashboard
python3 control_panel.py

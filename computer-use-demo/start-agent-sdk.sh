#!/bin/bash

# Start Computer Use Demo with Agent SDK integration
# This script launches the webui with all Agent SDK features enabled

set -e

echo "================================================"
echo "  Claude Computer Use - Agent SDK Edition"
echo "================================================"
echo ""
echo "Features enabled:"
echo "  ✓ Session persistence (saved in ~/.claude/projects/)"
echo "  ✓ Automatic verification (visual + structural)"
echo "  ✓ Subagent coordination (parallel execution)"
echo "  ✓ Context management (auto-compaction)"
echo "  ✓ Error recovery (automatic retry)"
echo "  ✓ Convention learning (CLAUDE.md)"
echo ""
echo "Configuration: .claude/settings.json"
echo "Agent definitions: .claude/agents/"
echo ""
echo "Starting webui on http://localhost:8000"
echo "================================================"
echo ""

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ] && [ ! -f ~/.anthropic/api_key ]; then
    echo "⚠️  Warning: No Anthropic API key found!"
    echo "   Set ANTHROPIC_API_KEY or create ~/.anthropic/api_key"
    echo ""
fi

# Load Hetzner API token from .env file if present
if [ -f "hetzner-deploy/.env" ]; then
    source hetzner-deploy/.env
    echo "✓ Loaded Hetzner API token from hetzner-deploy/.env"
fi

# Start VNC server first
echo "Launching VNC server..."
./start-vnc.sh &
VNC_PID=$!

# Run the webui
cd "$(dirname "$0")"
source .venv/bin/activate
python3 -m computer_use_demo.webui


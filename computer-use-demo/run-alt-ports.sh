#!/bin/bash
set -e

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  Warning: ANTHROPIC_API_KEY not set"
    echo "Please set it with: export ANTHROPIC_API_KEY=your_api_key"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "🚀 Starting Computer Use Demo (Alternative Ports)..."
echo ""
echo "Access points:"
echo "  Main Interface: http://localhost:8082"
echo "  Chat Only:      http://localhost:8502"
echo "  Desktop Only:   http://localhost:6082/vnc.html"
echo "  VNC Client:     vnc://localhost:5902"
echo ""

docker run \
    -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
    -v $HOME/.anthropic:/home/computeruse/.anthropic \
    -p 5902:5900 \
    -p 8502:8501 \
    -p 6082:6080 \
    -p 8082:8080 \
    -it computer-use-demo:local

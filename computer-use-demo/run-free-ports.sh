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

echo "🚀 Starting Computer Use Demo (Free Ports)..."
echo ""
echo "Access points:"
echo "  Main Interface: http://localhost:9080"
echo "  Chat Only:      http://localhost:9501"
echo "  Desktop Only:   http://localhost:9060/vnc.html"
echo "  VNC Client:     vnc://localhost:9900"
echo ""

docker run \
    -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
    -v $HOME/.anthropic:/home/computeruse/.anthropic \
    -p 9900:5900 \
    -p 9501:8501 \
    -p 9060:6080 \
    -p 9080:8080 \
    -it computer-use-demo:local

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

echo "🚀 Starting Computer Use Demo..."
echo ""
echo "Access points:"
echo "  Main Interface: http://localhost:8080"
echo "  Chat Only:      http://localhost:8501"
echo "  Desktop Only:   http://localhost:6080/vnc.html"
echo "  VNC Client:     vnc://localhost:5900"
echo ""

docker run \
    -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
    -v $HOME/.anthropic:/home/computeruse/.anthropic \
    -p 5900:5900 \
    -p 8501:8501 \
    -p 6080:6080 \
    -p 8080:8080 \
    -it computer-use-demo:local

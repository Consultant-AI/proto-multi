#!/bin/bash

# Build Docker image using x86_64 platform emulation
# This allows real Google Chrome to be installed even on ARM64 Macs
# Docker Desktop provides automatic emulation via QEMU

echo "Building container for x86_64 platform (emulated on ARM64)..."
echo "This may take 10-15 minutes on Apple Silicon Macs due to emulation..."

cd "$(dirname "$0")"

docker build --platform linux/amd64 . -t computer-use-demo:local

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build complete!"
    echo ""
    echo "Run with: ./run.sh"
    echo "Or with free ports: ./run-free-ports.sh"
else
    echo ""
    echo "❌ Build failed"
    exit 1
fi

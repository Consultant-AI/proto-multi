#!/bin/bash
set -e

echo "🔨 Building Docker image..."
docker build . -t computer-use-demo:local

echo ""
echo "✅ Build complete!"
echo ""
echo "To run the container, use:"
echo ""
echo "export ANTHROPIC_API_KEY=your_api_key"
echo "docker run \\"
echo "    -e ANTHROPIC_API_KEY=\$ANTHROPIC_API_KEY \\"
echo "    -v \$HOME/.anthropic:/home/computeruse/.anthropic \\"
echo "    -p 5900:5900 \\"
echo "    -p 8501:8501 \\"
echo "    -p 6080:6080 \\"
echo "    -p 8080:8080 \\"
echo "    -it computer-use-demo:local"
echo ""
echo "Or run: ./run.sh"

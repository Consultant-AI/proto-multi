#!/bin/bash
# Start the Hetzner Control Panel

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}===================================${NC}"
echo -e "${BLUE}Hetzner Control Panel${NC}"
echo -e "${BLUE}===================================${NC}"
echo ""

# Check for required environment variables
if [ -z "$HETZNER_API_TOKEN" ]; then
    echo -e "${RED}Error: HETZNER_API_TOKEN not set${NC}"
    echo ""
    echo "Run: export HETZNER_API_TOKEN=your-token-here"
    exit 1
fi

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${RED}Error: ANTHROPIC_API_KEY not set${NC}"
    echo ""
    echo "Run: export ANTHROPIC_API_KEY=your-key-here"
    exit 1
fi

# Install dependencies if needed
python3 -c "import flask" 2>/dev/null || {
    echo "Installing Flask..."
    pip3 install flask
}

echo -e "${GREEN}Starting control panel...${NC}"
echo ""
echo -e "${GREEN}Access at: http://localhost:5500${NC}"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start the control panel
python3 control_panel.py

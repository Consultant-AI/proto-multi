#!/bin/bash
# Quick deployment script for Hetzner Cloud

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}===================================${NC}"
echo -e "${BLUE}Hetzner Cloud Computer Use Deploy${NC}"
echo -e "${BLUE}===================================${NC}"
echo ""

# Check for required environment variables
if [ -z "$HETZNER_API_TOKEN" ]; then
    echo -e "${RED}Error: HETZNER_API_TOKEN not set${NC}"
    echo ""
    echo "Get your API token from: https://console.hetzner.cloud/"
    echo "Then run: export HETZNER_API_TOKEN=your-token-here"
    exit 1
fi

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${RED}Error: ANTHROPIC_API_KEY not set${NC}"
    echo ""
    echo "Get your API key from: https://console.anthropic.com/"
    echo "Then run: export ANTHROPIC_API_KEY=your-key-here"
    exit 1
fi

# Install dependencies
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 not found${NC}"
    exit 1
fi

# Check for requests library
python3 -c "import requests" 2>/dev/null || {
    echo "Installing required Python packages..."
    pip3 install requests
}

# Parse arguments
INSTANCE_NAME="computer-use-$(date +%s)"
SNAPSHOT_ID=""
COMMAND="create"

while [[ $# -gt 0 ]]; do
    case $1 in
        --name)
            INSTANCE_NAME="$2"
            shift 2
            ;;
        --snapshot)
            SNAPSHOT_ID="$2"
            shift 2
            ;;
        --list)
            COMMAND="list"
            shift
            ;;
        --list-snapshots)
            COMMAND="list-snapshots"
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Execute command
case $COMMAND in
    create)
        if [ -n "$SNAPSHOT_ID" ]; then
            echo -e "${GREEN}Creating instance from snapshot ${SNAPSHOT_ID}...${NC}"
            python3 hetzner_manager.py create --name "$INSTANCE_NAME" --snapshot "$SNAPSHOT_ID"
        else
            echo -e "${GREEN}Creating fresh instance...${NC}"
            python3 hetzner_manager.py create --name "$INSTANCE_NAME" --api-key "$ANTHROPIC_API_KEY"
        fi

        echo ""
        echo -e "${GREEN}✅ Deployment complete!${NC}"
        echo ""
        echo "Wait 2-3 minutes for Docker containers to start, then access:"
        echo ""
        ;;
    list)
        echo -e "${GREEN}Listing instances...${NC}"
        echo ""
        python3 hetzner_manager.py list
        ;;
    list-snapshots)
        echo -e "${GREEN}Listing snapshots...${NC}"
        echo ""
        python3 hetzner_manager.py list-snapshots
        ;;
esac

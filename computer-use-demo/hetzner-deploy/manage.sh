#!/bin/bash
# Instance management script - start, stop, snapshot, clone

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

if [ -z "$HETZNER_API_TOKEN" ]; then
    echo -e "${RED}Error: HETZNER_API_TOKEN not set${NC}"
    exit 1
fi

# Check for requests library
python3 -c "import requests" 2>/dev/null || {
    echo "Installing required Python packages..."
    pip3 install requests
}

show_help() {
    echo "Usage: ./manage.sh <command> [options]"
    echo ""
    echo "Commands:"
    echo "  start <instance-id>              Start a stopped instance"
    echo "  stop <instance-id>               Stop a running instance (saves money)"
    echo "  delete <instance-id>             Delete an instance"
    echo "  snapshot <instance-id> <desc>    Create snapshot of instance"
    echo "  clone <snapshot-id> <name>       Create new instance from snapshot"
    echo "  list                             List all instances"
    echo "  list-snapshots                   List all snapshots"
    echo ""
    echo "Examples:"
    echo "  ./manage.sh list"
    echo "  ./manage.sh stop 12345"
    echo "  ./manage.sh snapshot 12345 'with-chrome-extensions'"
    echo "  ./manage.sh clone 67890 my-dev-instance"
}

COMMAND=$1

case $COMMAND in
    start)
        if [ -z "$2" ]; then
            echo -e "${RED}Error: instance-id required${NC}"
            show_help
            exit 1
        fi
        python3 hetzner_manager.py start "$2"
        ;;
    stop)
        if [ -z "$2" ]; then
            echo -e "${RED}Error: instance-id required${NC}"
            show_help
            exit 1
        fi
        python3 hetzner_manager.py stop "$2"
        ;;
    delete)
        if [ -z "$2" ]; then
            echo -e "${RED}Error: instance-id required${NC}"
            show_help
            exit 1
        fi
        echo -e "${RED}⚠️  This will permanently delete instance $2${NC}"
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            python3 hetzner_manager.py delete "$2"
        else
            echo "Cancelled"
        fi
        ;;
    snapshot)
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo -e "${RED}Error: instance-id and description required${NC}"
            show_help
            exit 1
        fi
        python3 hetzner_manager.py snapshot "$2" --description "$3"
        ;;
    clone)
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo -e "${RED}Error: snapshot-id and name required${NC}"
            show_help
            exit 1
        fi
        python3 hetzner_manager.py create --name "$3" --snapshot "$2"
        ;;
    list)
        python3 hetzner_manager.py list
        ;;
    list-snapshots)
        python3 hetzner_manager.py list-snapshots
        ;;
    *)
        show_help
        ;;
esac

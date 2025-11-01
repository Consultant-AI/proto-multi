#!/bin/bash
# Fix API key on a snapshot-based instance

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <instance-ip> <api-key>"
    exit 1
fi

INSTANCE_IP=$1
API_KEY=$2

echo "🔧 Fixing API key on instance $INSTANCE_IP..."

# Update docker-compose.yml with new API key
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$INSTANCE_IP <<EOF
cd /opt/proto-multi/computer-use-demo

# Update API key in docker-compose.yml
sed -i 's/ANTHROPIC_API_KEY=.*/ANTHROPIC_API_KEY=$API_KEY/' docker-compose.yml

# Restart the service
systemctl restart computer-use-demo.service

# Wait for services
sleep 10

# Check status
docker compose ps

echo "✅ API key updated and services restarted"
EOF

echo "✅ Done! Services should be available in ~30 seconds"
echo "   Chrome: http://$INSTANCE_IP:8080"
echo "   Chat: http://$INSTANCE_IP:8501"

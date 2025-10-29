#!/bin/bash
# Setup automatic daily snapshots on the Hetzner instance

set -e

if [ -z "$1" ]; then
    echo "Usage: ./setup-auto-snapshot.sh <instance-id>"
    echo ""
    echo "This will setup a cron job on the instance to:"
    echo "  - Create daily snapshots at 3 AM"
    echo "  - Keep last 7 snapshots (1 week)"
    echo "  - Auto-delete old snapshots"
    exit 1
fi

INSTANCE_ID=$1

echo "Setting up automatic snapshots for instance $INSTANCE_ID..."

# Create cron script that will run on the instance
cat > /tmp/setup_cron.sh <<'EOFCRON'
#!/bin/bash
# Install on the Hetzner instance

# Install Python and dependencies (if not already)
apt-get update
apt-get install -y python3 python3-pip
pip3 install requests

# Create snapshot directory
mkdir -p /opt/auto-snapshot
cd /opt/auto-snapshot

# Download snapshot script
curl -o auto_snapshot.py https://raw.githubusercontent.com/Consultant-AI/proto-multi/main/computer-use-demo/hetzner-deploy/auto_snapshot.py
curl -o hetzner_manager.py https://raw.githubusercontent.com/Consultant-AI/proto-multi/main/computer-use-demo/hetzner-deploy/hetzner_manager.py
chmod +x auto_snapshot.py

# Create cron job for daily snapshots at 3 AM
cat > /etc/cron.d/auto-snapshot <<EOF
# Daily automatic snapshots at 3 AM
0 3 * * * root HETZNER_API_TOKEN="$HETZNER_API_TOKEN" HETZNER_INSTANCE_ID="$HETZNER_INSTANCE_ID" /usr/bin/python3 /opt/auto-snapshot/auto_snapshot.py --keep-last 7 >> /var/log/auto-snapshot.log 2>&1
EOF

chmod 644 /etc/cron.d/auto-snapshot

echo "✅ Automatic snapshots configured!"
echo "   Schedule: Daily at 3 AM"
echo "   Retention: Last 7 snapshots"
echo "   Logs: /var/log/auto-snapshot.log"
EOFCRON

chmod +x /tmp/setup_cron.sh

# Get instance IP
INSTANCE_IP=$(python3 -c "
from hetzner_manager import HetznerManager
import os
m = HetznerManager(os.environ.get('HETZNER_API_TOKEN'))
server = m.get_instance($INSTANCE_ID)
print(server['public_net']['ipv4']['ip'])
")

echo ""
echo "Instance IP: $INSTANCE_IP"
echo ""
echo "To enable automatic snapshots, you need to:"
echo "1. SSH into the instance: ssh root@$INSTANCE_IP"
echo "2. Run the setup script that will be uploaded"
echo ""
echo "Or run this command to do it automatically:"
echo "  scp /tmp/setup_cron.sh root@$INSTANCE_IP:/tmp/"
echo "  ssh root@$INSTANCE_IP 'HETZNER_API_TOKEN=$HETZNER_API_TOKEN HETZNER_INSTANCE_ID=$INSTANCE_ID bash /tmp/setup_cron.sh'"
echo ""

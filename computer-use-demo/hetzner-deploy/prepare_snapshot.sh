#!/bin/bash
# Prepare instance for fast snapshot restore
# This script ensures Docker images are saved to disk so they don't need rebuilding

set -e

INSTANCE_IP=$1

if [ -z "$INSTANCE_IP" ]; then
    echo "Usage: ./prepare_snapshot.sh <instance-ip>"
    exit 1
fi

echo "=========================================="
echo "Preparing instance for snapshot"
echo "IP: $INSTANCE_IP"
echo "=========================================="
echo ""

# SSH is not configured, so we need to use cloud-init to prepare the instance
# Instead, we'll create a preparation script that can be run via user_data

cat << 'EOFPREP'
To prepare an instance for fast snapshot restore:

1. The instance must have Docker images already built
2. Docker images should be saved in /var/lib/docker
3. Containers can be stopped (they'll auto-restart from snapshot)

The issue: Hetzner snapshots capture disk but Docker images
are stored in overlay filesystems that may not persist properly.

Solution: Ensure docker-compose builds are complete before snapshotting.

Current approach:
- When creating fresh instance: Cloud-init builds everything (~10-15 min)
- When snapshotting: Disk is saved with partial Docker data
- When restoring: Docker rebuilds from scratch (~10-15 min) ❌

Better approach:
- Create instance and let it fully build (~10-15 min)
- Once services are running, THEN create snapshot
- Snapshot will include built Docker images
- Restore will just start existing containers (~1-2 min) ✅

EOFPREP

echo ""
echo "Checking if instance $INSTANCE_IP is fully ready for snapshotting..."
echo ""

# Check if services are responding (means Docker is fully built)
if curl -s -u admin:anthropic2024 --max-time 5 http://$INSTANCE_IP/ > /dev/null 2>&1; then
    echo "✅ Instance is ready!"
    echo "✅ Services are responding"
    echo "✅ Docker images are built"
    echo ""
    echo "This instance is ready to be snapshotted via the dashboard."
    echo "Restored instances will boot in ~1-2 minutes."
else
    echo "⚠️  Instance is NOT ready yet"
    echo "⚠️  Services not responding"
    echo "⚠️  Docker is still building"
    echo ""
    echo "Wait for services to be fully up before creating snapshot."
    echo "Check dashboard - wait for 'Services Ready' status."
fi

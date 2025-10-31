#!/usr/bin/env python3
"""
Hetzner Cloud Manager for Computer Use Demo
Manages instances, snapshots, and cloning
"""

import os
import sys
import time
import requests
from typing import Optional, Dict, List
import json


class HetznerManager:
    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or os.environ.get('HETZNER_API_TOKEN')
        if not self.api_token:
            raise ValueError("HETZNER_API_TOKEN environment variable not set")

        self.base_url = "https://api.hetzner.cloud/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make API request to Hetzner"""
        url = f"{self.base_url}/{endpoint}"
        response = requests.request(method, url, headers=self.headers, json=data)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"API Error: {response.text}")
            raise
        return response.json()

    def create_instance(
        self,
        name: str,
        server_type: str = "cx22",  # 2 vCPU, 4GB RAM, €4.49/month
        location: str = "nbg1",  # Nuremberg, Germany - use 'hel1' for Finland, 'fsn1' for Germany
        image: str = "ubuntu-24.04",
        ssh_keys: Optional[List[str]] = None,
        user_data: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None
    ) -> Dict:
        """Create a new Hetzner instance"""

        data = {
            "name": name,
            "server_type": server_type,
            "location": location,
            "image": image,
            "start_after_create": True,
            "labels": labels or {},
        }

        if ssh_keys:
            data["ssh_keys"] = ssh_keys

        if user_data:
            data["user_data"] = user_data

        print(f"Creating instance '{name}'...")
        result = self._request("POST", "servers", data)
        server = result["server"]

        # Wait for server to be running
        print(f"Waiting for instance to start...")
        while True:
            status = self.get_instance_status(server["id"])
            if status == "running":
                break
            time.sleep(2)

        print(f"✅ Instance created: {server['name']}")
        print(f"   IP: {server['public_net']['ipv4']['ip']}")
        print(f"   ID: {server['id']}")

        return server

    def list_instances(self, label_selector: Optional[str] = None) -> List[Dict]:
        """List all instances"""
        endpoint = "servers"
        if label_selector:
            endpoint += f"?label_selector={label_selector}"

        result = self._request("GET", endpoint)
        return result["servers"]

    def get_instance(self, instance_id: int) -> Dict:
        """Get instance details"""
        result = self._request("GET", f"servers/{instance_id}")
        return result["server"]

    def get_instance_status(self, instance_id: int) -> str:
        """Get instance status"""
        server = self.get_instance(instance_id)
        return server["status"]

    def start_instance(self, instance_id: int) -> Dict:
        """Start a stopped instance"""
        print(f"Starting instance {instance_id}...")
        result = self._request("POST", f"servers/{instance_id}/actions/poweron")

        # Wait for running
        while True:
            status = self.get_instance_status(instance_id)
            if status == "running":
                break
            time.sleep(2)

        server = self.get_instance(instance_id)
        print(f"✅ Instance started: {server['public_net']['ipv4']['ip']}")
        return server

    def stop_instance(self, instance_id: int) -> None:
        """Stop a running instance (graceful shutdown)"""
        print(f"Stopping instance {instance_id}...")
        self._request("POST", f"servers/{instance_id}/actions/shutdown")

        # Wait for stopped
        while True:
            status = self.get_instance_status(instance_id)
            if status == "off":
                break
            time.sleep(2)

        print(f"✅ Instance stopped (hourly billing paused)")

    def delete_instance(self, instance_id: int) -> None:
        """Delete an instance"""
        print(f"Deleting instance {instance_id}...")
        self._request("DELETE", f"servers/{instance_id}")
        print(f"✅ Instance deleted")

    def create_snapshot(self, instance_id: int, description: str) -> Dict:
        """Create snapshot of instance (can be running or stopped)"""
        print(f"Creating snapshot of instance {instance_id}...")

        data = {
            "description": description,
            "labels": {
                "created_by": "computer-use-demo",
                "source_server": str(instance_id)
            }
        }

        result = self._request("POST", f"servers/{instance_id}/actions/create_image", data)
        image_id = result["image"]["id"]

        # Wait for snapshot to complete
        while True:
            action = self._request("GET", f"images/{image_id}")
            if action["image"]["status"] == "available":
                break
            print("  Snapshot in progress...")
            time.sleep(5)

        print(f"✅ Snapshot created: {image_id}")
        return action["image"]

    def list_snapshots(self, label_selector: Optional[str] = None) -> List[Dict]:
        """List all snapshots"""
        endpoint = "images?type=snapshot"
        if label_selector:
            endpoint += f"&label_selector={label_selector}"

        result = self._request("GET", endpoint)
        return result["images"]

    def clone_from_snapshot(
        self,
        snapshot_id: int,
        name: str,
        server_type: str = "cx22",
        location: str = "nbg1"  # Nuremberg, Germany
    ) -> Dict:
        """Create new instance from snapshot"""
        print(f"Cloning instance from snapshot {snapshot_id}...")

        return self.create_instance(
            name=name,
            server_type=server_type,
            location=location,
            image=str(snapshot_id),
            labels={"cloned_from": str(snapshot_id)}
        )

    def get_instance_by_name(self, name: str) -> Optional[Dict]:
        """Get instance by name"""
        instances = self.list_instances()
        for instance in instances:
            if instance["name"] == name:
                return instance
        return None


def generate_cloud_init_script(anthropic_api_key: str, hetzner_api_token: str = None) -> str:
    """
    Generate cloud-init script for instance setup

    ⚠️ IMPORTANT: This ALWAYS builds from Consultant-AI/proto-multi repo

    WHY? The official Anthropic image has a bug in index.html:
    - Uses "localhost" instead of "window.location.hostname"
    - This breaks port 8080 when accessed remotely
    - Our repo has the FIXED index.html

    DO NOT change this to use ghcr.io/anthropics/anthropic-quickstarts!
    That image will NOT work correctly on Hetzner Cloud.
    """

    # Use environment variable if not provided
    if not hetzner_api_token:
        hetzner_api_token = os.environ.get('HETZNER_API_TOKEN', '')

    return f"""#!/bin/bash
set -e

# Update system
apt-get update
apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Install Docker Compose and git
apt-get install -y docker-compose-plugin git

# Clone the optimized repo with Chrome and fixes
cd /opt
git clone --depth 1 https://github.com/Consultant-AI/proto-multi.git
cd proto-multi/computer-use-demo

# Build the Docker image for x86_64 with proper settings
# Use BuildKit for better performance and increase timeout
export DOCKER_BUILDKIT=1
export BUILDKIT_STEP_LOG_MAX_SIZE=50000000
docker build \\
    --platform linux/amd64 \\
    --progress=plain \\
    --no-cache \\
    -t computer-use-demo:local \\
    . 2>&1 | tee /var/log/docker-build.log

# Check if build succeeded
if [ $? -ne 0 ]; then
    echo "ERROR: Docker build failed!" | tee -a /var/log/docker-build.log
    exit 1
fi

echo "✅ Docker build completed successfully"

# ========================================
# SECURITY SETUP
# ========================================
echo "🔒 Setting up security measures..."

# Setup firewall to prevent network scanning
echo "Setting up firewall rules..."
apt-get install -y iptables-persistent

# Flush existing rules
iptables -F
iptables -X

# Default policies - ALLOW outbound by default, but block specific dangerous ports
iptables -P INPUT ACCEPT
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Allow loopback
iptables -A OUTPUT -o lo -j ACCEPT
iptables -A INPUT -i lo -j ACCEPT

# Allow established connections
iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow incoming SSH (port 22)
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Allow incoming HTTP services (8080, 8501, 6080)
iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
iptables -A INPUT -p tcp --dport 8501 -j ACCEPT
iptables -A INPUT -p tcp --dport 6080 -j ACCEPT
iptables -A INPUT -p tcp --dport 5900 -j ACCEPT

# BLOCK ALL VNC SCANNING PORTS (5900-5909) - CRITICAL FOR ABUSE PREVENTION!
iptables -I OUTPUT 1 -p tcp --dport 5900:5909 -m conntrack --ctstate NEW -j REJECT --reject-with tcp-reset
iptables -I OUTPUT 1 -p udp --dport 5900:5909 -j REJECT

# Block common attack/scanning ports OUTBOUND
iptables -A OUTPUT -p tcp --dport 23 -j REJECT       # Telnet
iptables -A OUTPUT -p tcp --dport 445 -j REJECT      # SMB
iptables -A OUTPUT -p tcp --dport 139 -j REJECT      # NetBIOS
iptables -A OUTPUT -p tcp --dport 3389 -j REJECT     # RDP

# Log blocked VNC connection attempts (for monitoring abuse prevention)
iptables -A OUTPUT -p tcp --dport 5900:5909 -m limit --limit 5/min -j LOG --log-prefix "BLOCKED-VNC-SCAN: " --log-level 4

# Save firewall rules
netfilter-persistent save

echo "✅ Firewall configured - VNC scanning blocked, all other traffic allowed"

# Create docker-compose.yml
cat > docker-compose.yml <<'EOFCOMPOSE'
version: '3.8'

services:
  computer-use:
    image: computer-use-demo:local
    platform: linux/amd64
    ports:
      - "8080:8080"  # noVNC
      - "8501:8501"  # Streamlit chat
      - "5900:5900"  # VNC
      - "6080:6080"  # noVNC alt port
    environment:
      - ANTHROPIC_API_KEY={anthropic_api_key}
    volumes:
      - computeruse-home:/home/computeruse
    restart: unless-stopped
    shm_size: 2gb

volumes:
  computeruse-home:
    driver: local
EOFCOMPOSE

# Create systemd service for auto-start on boot
cat > /etc/systemd/system/computer-use-demo.service <<'EOFSYSTEMD'
[Unit]
Description=Computer Use Demo Docker Compose
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/proto-multi/computer-use-demo
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOFSYSTEMD

# Enable and start the service
systemctl daemon-reload
systemctl enable computer-use-demo.service
systemctl start computer-use-demo.service

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 30

# Show status
docker compose ps

echo "=================================" | tee /root/setup-complete.txt
echo "✅ Computer Use Demo is ready!" | tee -a /root/setup-complete.txt
echo "=================================" | tee -a /root/setup-complete.txt
IP=$(curl -s http://169.254.169.254/hetzner/v1/metadata/public-ipv4)
echo "Chat Interface: http://$IP:8501" | tee -a /root/setup-complete.txt
echo "Chrome Desktop: http://$IP:8080" | tee -a /root/setup-complete.txt
echo "=================================" | tee -a /root/setup-complete.txt

# Setup automatic daily snapshots
echo "Setting up automatic snapshots..."
mkdir -p /opt/auto-snapshot
cd /opt/auto-snapshot

# Download snapshot scripts from GitHub
curl -sL -o auto_snapshot.py https://raw.githubusercontent.com/Consultant-AI/proto-multi/main/computer-use-demo/hetzner-deploy/auto_snapshot.py
curl -sL -o hetzner_manager.py https://raw.githubusercontent.com/Consultant-AI/proto-multi/main/computer-use-demo/hetzner-deploy/hetzner_manager.py
chmod +x auto_snapshot.py

# Get instance ID from metadata
INSTANCE_ID=$(curl -s http://169.254.169.254/hetzner/v1/metadata/instance-id)

# Create cron job for daily snapshots at 3 AM (keeps last 7 days)
cat > /etc/cron.d/auto-snapshot <<EOFCRON
# Automatic daily snapshots at 3 AM - keeps last 7 snapshots
0 3 * * * root HETZNER_API_TOKEN="{hetzner_api_token}" HETZNER_INSTANCE_ID="$INSTANCE_ID" /usr/bin/python3 /opt/auto-snapshot/auto_snapshot.py --keep-last 7 >> /var/log/auto-snapshot.log 2>&1
EOFCRON

chmod 644 /etc/cron.d/auto-snapshot

echo "✅ Automatic snapshots enabled!" | tee -a /root/setup-complete.txt
echo "   Schedule: Daily at 3 AM UTC" | tee -a /root/setup-complete.txt
echo "   Retention: Last 7 days" | tee -a /root/setup-complete.txt
echo "   Logs: /var/log/auto-snapshot.log" | tee -a /root/setup-complete.txt
"""


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Hetzner Cloud Manager for Computer Use Demo")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Create instance
    create_parser = subparsers.add_parser("create", help="Create new instance")
    create_parser.add_argument("--name", required=True, help="Instance name")
    create_parser.add_argument("--api-key", help="Anthropic API key")
    create_parser.add_argument("--snapshot", type=int, help="Clone from snapshot ID")

    # List instances
    subparsers.add_parser("list", help="List all instances")

    # Start instance
    start_parser = subparsers.add_parser("start", help="Start instance")
    start_parser.add_argument("id", type=int, help="Instance ID")

    # Stop instance
    stop_parser = subparsers.add_parser("stop", help="Stop instance")
    stop_parser.add_argument("id", type=int, help="Instance ID")

    # Delete instance
    delete_parser = subparsers.add_parser("delete", help="Delete instance")
    delete_parser.add_argument("id", type=int, help="Instance ID")

    # Create snapshot
    snapshot_parser = subparsers.add_parser("snapshot", help="Create snapshot")
    snapshot_parser.add_argument("id", type=int, help="Instance ID")
    snapshot_parser.add_argument("--description", required=True, help="Snapshot description")

    # List snapshots
    subparsers.add_parser("list-snapshots", help="List all snapshots")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    manager = HetznerManager()

    if args.command == "create":
        if args.snapshot:
            # Clone from snapshot
            server = manager.clone_from_snapshot(
                snapshot_id=args.snapshot,
                name=args.name
            )
        else:
            # Create new instance
            api_key = args.api_key or os.environ.get('ANTHROPIC_API_KEY')
            if not api_key:
                print("Error: ANTHROPIC_API_KEY required")
                sys.exit(1)

            user_data = generate_cloud_init_script(api_key, manager.api_token)
            server = manager.create_instance(
                name=args.name,
                user_data=user_data,
                labels={"app": "computer-use-demo"}
            )

        print(f"\n🌐 Access your instance:")
        print(f"   Chat: http://{server['public_net']['ipv4']['ip']}:8501")
        print(f"   Chrome: http://{server['public_net']['ipv4']['ip']}:8080")

    elif args.command == "list":
        instances = manager.list_instances(label_selector="app=computer-use-demo")
        if not instances:
            print("No instances found")
        else:
            for server in instances:
                status = server['status']
                ip = server['public_net']['ipv4']['ip']
                print(f"{server['id']}\t{server['name']}\t{status}\t{ip}")

    elif args.command == "start":
        server = manager.start_instance(args.id)
        print(f"\n🌐 Access your instance:")
        print(f"   Chat: http://{server['public_net']['ipv4']['ip']}:8501")
        print(f"   Chrome: http://{server['public_net']['ipv4']['ip']}:8080")

    elif args.command == "stop":
        manager.stop_instance(args.id)

    elif args.command == "delete":
        manager.delete_instance(args.id)

    elif args.command == "snapshot":
        manager.create_snapshot(args.id, args.description)

    elif args.command == "list-snapshots":
        snapshots = manager.list_snapshots(label_selector="created_by=computer-use-demo")
        if not snapshots:
            print("No snapshots found")
        else:
            for snapshot in snapshots:
                print(f"{snapshot['id']}\t{snapshot['description']}\t{snapshot['created']}")

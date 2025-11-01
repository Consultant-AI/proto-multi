#!/usr/bin/env python3
"""Simplified version that deploys without nginx auth"""
import os
import sys
from hetzner_manager import HetznerManager

def generate_simple_cloud_init(anthropic_api_key: str) -> str:
    """Generate simplified cloud-init without auth complexity"""
    return f"""#!/bin/bash
set -e
exec > >(tee /var/log/cloud-init-output.log)
exec 2>&1

echo "========== STARTING DEPLOYMENT =========="
date

# Update system
echo "Updating system..."
apt-get update
apt-get upgrade -y

# Install Docker
echo "Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Install Docker Compose
echo "Installing Docker Compose..."
apt-get install -y docker-compose-plugin git

# Clone repo
echo "Cloning repository..."
cd /opt
git clone --depth 1 https://github.com/Consultant-AI/proto-multi.git
cd proto-multi/computer-use-demo

# Build Docker image
echo "Building Docker image..."
export DOCKER_BUILDKIT=1
docker build --platform linux/amd64 -t computer-use-demo:local . 2>&1 | tee /var/log/docker-build.log

if [ $? -ne 0 ]; then
    echo "ERROR: Docker build failed!"
    exit 1
fi

echo "✅ Docker build completed"

# Create docker-compose.yml
cat > docker-compose.yml <<'EOFCOMPOSE'
version: '3.8'

services:
  computer-use:
    image: computer-use-demo:local
    platform: linux/amd64
    ports:
      - "8080:8080"
      - "8501:8501"
      - "5900:5900"
      - "6080:6080"
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

# Create systemd service
cat > /etc/systemd/system/computer-use-demo.service <<'EOFSYSTEMD'
[Unit]
Description=Computer Use Demo
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

# Start service
echo "Starting Docker service..."
systemctl daemon-reload
systemctl enable computer-use-demo.service
systemctl start computer-use-demo.service

# Wait and check
sleep 20
docker compose ps

echo "========== DEPLOYMENT COMPLETE =========="
IP=$(curl -s http://169.254.169.254/hetzner/v1/metadata/public-ipv4)
echo "Access at: http://$IP:8080"
date
"""

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--api-key", required=True)
    args = parser.parse_args()

    manager = HetznerManager()
    user_data = generate_simple_cloud_init(args.api_key)

    print("Creating instance with SIMPLIFIED deployment (no auth)...")
    server = manager.create_instance(
        name=args.name,
        user_data=user_data,
        labels={"app": "computer-use-demo", "version": "simple"}
    )

    print(f"\n✅ Instance created: {server['name']}")
    print(f"   IP: {server['public_net']['ipv4']['ip']}")
    print(f"   ID: {server['id']}")
    print(f"\n🌐 Access (in ~10 mins):")
    print(f"   Chrome: http://{server['public_net']['ipv4']['ip']}:8080")
    print(f"   Chat: http://{server['public_net']['ipv4']['ip']}:8501")

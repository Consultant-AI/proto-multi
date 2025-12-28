"""Cloud-init script generator for Hetzner instances with full auto-configuration."""

import os
from pathlib import Path
from typing import Optional


def generate_cloud_init_script(
    anthropic_api_key: str,
    hetzner_api_token: str = None,
    ssh_public_key: Optional[str] = None
) -> str:
    """
    Generate cloud-init script with full auto-configuration for Agent SDK deployment.

    Includes:
    - Docker installation
    - Repository clone
    - Agent SDK setup
    - VNC setup (x11vnc + noVNC)
    - SSH key configuration
    - Systemd service for auto-start
    """

    # Get SSH public key if not provided - try ed25519 first, then rsa
    if not ssh_public_key:
        for key_name in ["id_ed25519.pub", "id_rsa.pub"]:
            ssh_key_path = Path.home() / ".ssh" / key_name
            if ssh_key_path.exists():
                ssh_public_key = ssh_key_path.read_text().strip()
                break
        else:
            ssh_public_key = ""

    return f"""#!/bin/bash
set -e
exec > >(tee /var/log/cloud-init-output.log)
exec 2>&1

echo "========== HETZNER INSTANCE DEPLOYMENT START =========="
date

# Update system
echo "Updating system packages..."
apt-get update
apt-get upgrade -y

# Install Docker and dependencies
echo "Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

echo "Installing Docker Compose and dependencies..."
apt-get install -y docker-compose-plugin git curl wget openssh-server x11-utils

# Configure SSH
echo "Configuring SSH for passwordless authentication..."
mkdir -p /root/.ssh
chmod 700 /root/.ssh

# Add user's SSH public key
{f'echo "{ssh_public_key}" >> /root/.ssh/authorized_keys' if ssh_public_key else '# No SSH key provided'}
chmod 600 /root/.ssh/authorized_keys

# Update SSH config for key-only authentication (no password)
sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config
sed -i 's/^#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config
sed -i 's/^PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
echo "PasswordAuthentication no" >> /etc/ssh/sshd_config

# Disable password expiry for root (prevents "password expired" blocking)
chage -M -1 root
passwd -d root

systemctl restart ssh

# Clone repository
echo "Cloning proto-multi repository..."
cd /opt
git clone --depth 1 https://github.com/Consultant-AI/proto-multi.git
cd proto-multi/computer-use-demo

# Install additional X11 and VNC dependencies for Display
echo "Installing VNC and display server dependencies..."
apt-get install -y x11-apps xvfb xdotool wmctrl xclip

# Build Docker image with Agent SDK
echo "Building Docker image with Agent SDK..."
export DOCKER_BUILDKIT=1
export ANTHROPIC_API_KEY={anthropic_api_key}
export HETZNER_API_TOKEN={hetzner_api_token or ''}

docker build --platform linux/amd64 -t computer-use-demo:local . 2>&1 | tee /var/log/docker-build.log

if [ $? -ne 0 ]; then
    echo "ERROR: Docker build failed!"
    exit 1
fi

echo "✅ Docker build completed"

# Save Docker image for snapshot preservation
echo "Saving Docker image for snapshot preservation..."
docker save computer-use-demo:local -o /var/lib/docker-image-backup.tar
echo "✅ Docker image backed up"

# Create docker-compose.yml
cat > docker-compose.yml <<'EOFCOMPOSE'
version: '3.8'

services:
  computer-use:
    image: computer-use-demo:local
    platform: linux/amd64
    ports:
      - "0.0.0.0:8000:8000"    # Agent SDK API (public)
      - "0.0.0.0:5900:5900"    # VNC server (public)
      - "0.0.0.0:6080:6080"    # noVNC web interface (public)
    environment:
      - ANTHROPIC_API_KEY={anthropic_api_key}
      - HETZNER_API_TOKEN={hetzner_api_token or ''}
    volumes:
      - /tmp/.X11-unix:/tmp/.X11-unix:rw
      - /var/run/dbus:/var/run/dbus:rw
    ipc: host
    cap_add:
      - SYS_ADMIN
    security_opt:
      - seccomp=unconfined
    restart: unless-stopped

EOFCOMPOSE

# Create systemd service for auto-start
echo "Creating systemd service for auto-start..."
cat > /etc/systemd/system/computer-use-demo.service <<'EOFSYSTEMD'
[Unit]
Description=Computer Use Demo Agent SDK
After=docker.service
Requires=docker.service

[Service]
Type=simple
WorkingDirectory=/opt/proto-multi/computer-use-demo
ExecStart=/usr/bin/docker compose up
Restart=on-failure
RestartSec=10
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

[Install]
WantedBy=multi-user.target

EOFSYSTEMD

chmod 644 /etc/systemd/system/computer-use-demo.service

# Start services
echo "Starting Docker daemon and services..."
systemctl daemon-reload
systemctl enable computer-use-demo.service
systemctl start computer-use-demo.service

# Wait for services to start
echo "Waiting for services to be ready..."
sleep 10

# Check service status
echo "Checking service status..."
docker compose ps

echo "========== DEPLOYMENT COMPLETE =========="
date

echo "✅ Instance is ready!"
echo "   Agent SDK API: http://$(hostname -I | awk '{{print $1}}'):8000"
echo "   VNC Server: $(hostname -I | awk '{{print $1}}'):5900"
echo "   noVNC Web: http://$(hostname -I | awk '{{print $1}}'):6080"
echo ""
echo "📝 Note: This instance can be connected via SSH tunnel from the main UI."
"""

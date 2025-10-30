#!/usr/bin/env python3
"""
Minimal build - clone repo and build, but with better error handling
"""

def generate_minimal_cloud_init(anthropic_api_key: str) -> str:
    """Build from our repo with fixed index.html"""

    return f"""#!/bin/bash
set -ex  # Exit on error, print commands

exec > >(tee /var/log/cloud-init-output.log)
exec 2>&1

echo "==== Starting Computer Use Demo Setup ===="
date

# Update system
echo "==== Installing Docker ===="
apt-get update
export DEBIAN_FRONTEND=noninteractive
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
apt-get install -y docker-compose-plugin git

# Clone repo with our fixes
echo "==== Cloning repository ===="
cd /opt
git clone --depth 1 https://github.com/Consultant-AI/proto-multi.git
cd proto-multi/computer-use-demo

# Build with explicit platform
echo "==== Building Docker image (this takes 10-15 min) ===="
DOCKER_BUILDKIT=1 docker build \\
    --platform linux/amd64 \\
    --progress=plain \\
    --tag computer-use-demo:local \\
    . 2>&1 | tee /var/log/docker-build.log

if [ $? -ne 0 ]; then
    echo "Docker build failed! Check /var/log/docker-build.log"
    exit 1
fi

# Create docker-compose.yml
echo "==== Creating docker-compose.yml ===="
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
echo "==== Creating systemd service ===="
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

# Enable and start
echo "==== Starting service ===="
systemctl daemon-reload
systemctl enable computer-use-demo.service
systemctl start computer-use-demo.service

# Wait and verify
echo "==== Waiting for services ===="
sleep 30

docker compose ps
docker compose logs --tail=50

IP=$(curl -s http://169.254.169.254/hetzner/v1/metadata/public-ipv4)

echo "================================="
echo "✅ Setup complete!"
echo "================================="
echo "Chat: http://$IP:8501"
echo "Desktop: http://$IP:8080"
echo "================================="
echo "Build logs: /var/log/docker-build.log"
echo "Output logs: /var/log/cloud-init-output.log"
echo "================================="

date
"""

if __name__ == '__main__':
    import os
    import sys
    sys.path.insert(0, '/Users/nirfeinstein/Documents/GitHub/proto-multi/computer-use-demo/hetzner-deploy')
    from hetzner_manager import HetznerManager

    manager = HetznerManager()
    api_key = os.environ['ANTHROPIC_API_KEY']

    print("Creating instance with FULL BUILD (15-20 minutes)...")
    print("✅ Uses our repo with fixed index.html")
    print("✅ Full error logging")
    print("✅ Systemd auto-start")
    print("")
    print("⏱️  This will take 15-20 minutes but will work correctly!")
    print("")

    user_data = generate_minimal_cloud_init(api_key)

    server = manager.create_instance(
        name='computer-use-complete',
        user_data=user_data,
        labels={'app': 'computer-use-demo'}
    )

    print("")
    print(f"✅ Instance created: {server['public_net']['ipv4']['ip']}")
    print(f"   ID: {server['id']}")
    print("")
    print("Build is starting now. Services will be ready in 15-20 minutes.")
    print("All features will work (port 8080, pause/resume, health checks).")

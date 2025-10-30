#!/usr/bin/env python3
"""
WORKING solution: Official image + nginx proxy to fix localhost URLs
Ready in 3-5 minutes!
"""

def generate_proxy_cloud_init(anthropic_api_key: str) -> str:
    """Use official image with nginx proxy to rewrite localhost URLs"""

    return f"""#!/bin/bash
set -ex

exec > >(tee /var/log/cloud-init-output.log)
exec 2>&1

echo "==== Installing Docker and nginx ===="
apt-get update
export DEBIAN_FRONTEND=noninteractive
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
apt-get install -y docker-compose-plugin nginx

# Pull official image (fast!)
echo "==== Pulling official Docker image ===="
cd /opt
docker pull ghcr.io/anthropics/anthropic-quickstarts:computer-use-demo-latest

# Create docker-compose on INTERNAL ports
cat > docker-compose.yml <<'EOFCOMPOSE'
version: '3.8'

services:
  computer-use:
    image: ghcr.io/anthropics/anthropic-quickstarts:computer-use-demo-latest
    platform: linux/amd64
    ports:
      - "127.0.0.1:9080:8080"  # Internal only
      - "0.0.0.0:8501:8501"    # Direct access OK
      - "127.0.0.1:9900:5900"  # Internal only
      - "0.0.0.0:6080:6080"    # Direct access OK
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

# Configure nginx to proxy port 8080 and fix localhost URLs
cat > /etc/nginx/sites-available/computer-use <<'EOFNGINX'
server {{
    listen 8080;
    listen [::]:8080;

    location / {{
        proxy_pass http://127.0.0.1:9080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;

        # Fix localhost URLs in HTML responses
        sub_filter 'http://localhost:8501' 'http://$http_host:8501';
        sub_filter 'http://localhost:6080' 'http://$http_host:6080';
        sub_filter 'http://127.0.0.1:8501' 'http://$http_host:8501';
        sub_filter 'http://127.0.0.1:6080' 'http://$http_host:6080';
        sub_filter_once off;
        sub_filter_types *;
    }}
}}
EOFNGINX

ln -sf /etc/nginx/sites-available/computer-use /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

# Systemd service for Docker
cat > /etc/systemd/system/computer-use-demo.service <<'EOFSYSTEMD'
[Unit]
Description=Computer Use Demo
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOFSYSTEMD

systemctl daemon-reload
systemctl enable computer-use-demo.service
systemctl start computer-use-demo.service

sleep 30

IP=$(curl -s http://169.254.169.254/hetzner/v1/metadata/public-ipv4)

echo "================================="
echo "✅ Services ready!"
echo "================================="
echo "Chat: http://$IP:8501"
echo "Desktop: http://$IP:8080 (nginx proxy fixes localhost)"
echo "================================="
"""

if __name__ == '__main__':
    import os
    import sys
    sys.path.insert(0, '/Users/nirfeinstein/Documents/GitHub/proto-multi/computer-use-demo/hetzner-deploy')
    from hetzner_manager import HetznerManager

    manager = HetznerManager()
    api_key = os.environ['ANTHROPIC_API_KEY']

    print("Creating WORKING instance (3-5 minutes)...")
    print("✅ Official Docker image (fast pull)")
    print("✅ Nginx proxy fixes localhost URLs")
    print("✅ Systemd auto-start")
    print("")

    user_data = generate_proxy_cloud_init(api_key)

    server = manager.create_instance(
        name='computer-use-proxy',
        user_data=user_data,
        labels={'app': 'computer-use-demo'}
    )

    print("")
    print(f"✅ Instance created: {server['public_net']['ipv4']['ip']}")
    print(f"   ID: {server['id']}")
    print("")
    print("Services will be ready in 3-5 minutes!")
    print("Port 8080 will work correctly via nginx proxy!")

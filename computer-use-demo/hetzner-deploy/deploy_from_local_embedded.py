#!/usr/bin/env python3
"""
Deploy from LOCAL files by embedding them as base64 in cloud-init
No SSH needed - everything embedded in cloud-init script
"""

import os
import sys
import time
import subprocess
import base64
from hetzner_manager import HetznerManager

def create_tarball_and_encode():
    """Create tarball of local files and base64 encode it"""
    local_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print(f"Creating tarball from: {local_path}")

    # Create tarball
    result = subprocess.run([
        "tar", "-czf", "/tmp/computer-use-local.tar.gz",
        "--exclude", "hetzner-deploy",
        "--exclude", ".git",
        "--exclude", "__pycache__",
        "--exclude", "*.pyc",
        "-C", os.path.dirname(local_path),
        "computer-use-demo"
    ], capture_output=True)

    if result.returncode != 0:
        print(f"Error creating tarball: {result.stderr.decode()}")
        return None

    # Base64 encode
    result = subprocess.run([
        "base64", "-i", "/tmp/computer-use-local.tar.gz"
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error encoding: {result.stderr}")
        return None

    encoded = result.stdout.strip()
    print(f"✅ Created encoded tarball ({len(encoded)} bytes)")
    return encoded

def generate_cloud_init_with_embedded_files(anthropic_api_key: str, tarball_b64: str) -> str:
    """Generate cloud-init with embedded local files"""
    return f"""#!/bin/bash
set -e
exec > >(tee /var/log/cloud-init-output.log)
exec 2>&1

echo "========== DEPLOYING FROM LOCAL FILES =========="

# Update system
apt-get update
apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Install Docker Compose and other tools
apt-get install -y docker-compose-plugin nginx apache2-utils

# Extract embedded files
echo "Extracting local files..."
cd /opt
cat > computer-use-local.tar.gz.b64 <<'EOFARCHIVE'
{tarball_b64}
EOFARCHIVE

base64 -d computer-use-local.tar.gz.b64 > computer-use-local.tar.gz
tar -xzf computer-use-local.tar.gz
rm computer-use-local.tar.gz computer-use-local.tar.gz.b64

cd /opt/computer-use-demo

echo "Building Docker image..."
export DOCKER_BUILDKIT=1
docker build --platform linux/amd64 -t computer-use-demo:local . 2>&1 | tee /var/log/docker-build.log

# Create docker-compose.yml
cat > docker-compose.yml <<'EOFCOMPOSE'
version: '3.8'

services:
  computer-use:
    image: computer-use-demo:local
    platform: linux/amd64
    ports:
      - "127.0.0.1:8080:8080"
      - "127.0.0.1:8501:8501"
      - "127.0.0.1:5900:5900"
      - "127.0.0.1:6080:6080"
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

# Start services
echo "Starting services..."
docker compose up -d

# Wait for Docker to be ready
sleep 10

# Configure nginx with authentication
echo "Configuring nginx..."
echo 'anthropic2024' | htpasswd -ci /etc/nginx/.htpasswd admin

cat > /etc/nginx/sites-available/computer-use <<'EOFNGINX'
server {{
    listen 80;
    server_name _;

    location = / {{
        auth_basic "Computer Use Demo";
        auth_basic_user_file /etc/nginx/.htpasswd;
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }}

    location ~ ^/(static|assets|css|js)/ {{
        auth_basic "Computer Use Demo";
        auth_basic_user_file /etc/nginx/.htpasswd;
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }}

    location /PORT8501/ {{
        auth_basic off;
        rewrite ^/PORT8501/(.*) /$1 break;
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }}

    location /_stcore/ {{
        auth_basic off;
        proxy_pass http://127.0.0.1:8501/_stcore/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }}

    location /healthz {{
        auth_basic off;
        proxy_pass http://127.0.0.1:8501/healthz;
    }}

    location /PORT6080/ {{
        auth_basic off;
        rewrite ^/PORT6080/(.*) /$1 break;
        proxy_pass http://127.0.0.1:6080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }}

    location /websockify {{
        auth_basic off;
        proxy_pass http://127.0.0.1:6080/websockify;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }}
}}
EOFNGINX

ln -sf /etc/nginx/sites-available/computer-use /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
systemctl restart nginx
systemctl enable nginx

echo "========== LOCAL DEPLOYMENT COMPLETE =========="
IP=$(curl -s http://169.254.169.254/hetzner/v1/metadata/public-ipv4)
echo "✅ Deployed from local files"
echo "🌐 Access at: http://$IP/"
echo "👤 Username: admin"
echo "🔑 Password: anthropic2024"
"""

def main():
    # Check environment
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    print("\n=== Creating tarball from local files ===")
    tarball_b64 = create_tarball_and_encode()
    if not tarball_b64:
        print("❌ Failed to create tarball")
        sys.exit(1)

    print("\n=== Creating Hetzner instance ===")
    manager = HetznerManager()

    user_data = generate_cloud_init_with_embedded_files(api_key, tarball_b64)
    name = f"local-embedded-{int(time.time())}"

    server = manager.create_instance(
        name=name,
        user_data=user_data,
        labels={"app": "computer-use-demo", "deploy-type": "local-embedded"}
    )

    ip = server['public_net']['ipv4']['ip']
    server_id = server['id']

    print(f"✅ Instance created: {name}")
    print(f"   IP: {ip}")
    print(f"   ID: {server_id}")

    print("\n" + "="*60)
    print("✅ DEPLOYING FROM YOUR LOCAL FILES")
    print("="*60)
    print(f"\n🌐 Will be ready at: http://{ip}/")
    print(f"👤 Username: admin")
    print(f"🔑 Password: anthropic2024")
    print("\nDeployment takes ~10-12 minutes")
    print("All features from your LOCAL files will work!")
    print("Chrome, iframes, everything as it works locally.")

if __name__ == '__main__':
    main()

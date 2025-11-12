#!/usr/bin/env python3
"""
Deploy from LOCAL files instead of GitHub
This ensures Chrome and all features work exactly as in local development
"""

import os
import sys
import time
import subprocess
from hetzner_manager import HetznerManager, generate_cloud_init_script

def generate_minimal_cloud_init(anthropic_api_key: str, hetzner_api_token: str = None) -> str:
    """Generate minimal cloud-init that just prepares the server"""
    return f"""#!/bin/bash
set -e
exec > >(tee /var/log/cloud-init-output.log)
exec 2>&1

echo "========== MINIMAL SETUP - WAITING FOR LOCAL FILES =========="

# Update system
apt-get update
apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Install Docker Compose
apt-get install -y docker-compose-plugin

# Create working directory
mkdir -p /opt/computer-use-demo
chown -R root:root /opt/computer-use-demo

echo "✅ Server ready for local file upload"
echo "Waiting for files to be uploaded via SCP..."
"""

def wait_for_ssh(ip: str, max_attempts=30):
    """Wait for SSH to be available"""
    print(f"Waiting for SSH on {ip}...")
    for i in range(max_attempts):
        result = subprocess.run(
            ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=5",
             f"root@{ip}", "echo 'SSH ready'"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✅ SSH ready on {ip}")
            return True
        print(f"  Attempt {i+1}/{max_attempts}...")
        time.sleep(10)
    return False

def upload_local_files(ip: str, local_path: str):
    """Upload local computer-use-demo directory to server"""
    print(f"\nUploading local files from {local_path} to {ip}...")

    # Use rsync to upload the directory
    result = subprocess.run([
        "rsync", "-avz", "--progress",
        "--exclude", "hetzner-deploy",
        "--exclude", ".git",
        "--exclude", "__pycache__",
        "--exclude", "*.pyc",
        f"{local_path}/",
        f"root@{ip}:/opt/computer-use-demo/"
    ])

    if result.returncode == 0:
        print("✅ Files uploaded successfully")
        return True
    else:
        print("❌ File upload failed")
        return False

def build_and_start(ip: str, anthropic_api_key: str):
    """Build Docker image and start services on remote server"""
    print(f"\nBuilding and starting services on {ip}...")

    build_script = f"""
cd /opt/computer-use-demo

echo "Building Docker image..."
export DOCKER_BUILDKIT=1
docker build --platform linux/amd64 -t computer-use-demo:local .

echo "Creating docker-compose.yml..."
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

echo "Starting services..."
systemctl daemon-reload
docker compose up -d

echo "Installing nginx..."
apt-get install -y nginx apache2-utils

echo "Creating password..."
echo 'anthropic2024' | htpasswd -ci /etc/nginx/.htpasswd admin

echo "Configuring nginx..."
cat > /etc/nginx/sites-available/computer-use <<'EOFNGINX'
server {{
    listen 80;
    server_name _;

    location = / {{
        auth_basic "Computer Use Demo";
        auth_basic_user_file /etc/nginx/.htpasswd;
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \\$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \\$host;
        proxy_read_timeout 86400;
    }}

    location ~ ^/(static|assets|css|js)/ {{
        auth_basic "Computer Use Demo";
        auth_basic_user_file /etc/nginx/.htpasswd;
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Host \\$host;
    }}

    location /PORT8501/ {{
        auth_basic off;
        rewrite ^/PORT8501/(.*) /\\$1 break;
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \\$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \\$host;
        proxy_read_timeout 86400;
    }}

    location /_stcore/ {{
        auth_basic off;
        proxy_pass http://127.0.0.1:8501/_stcore/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \\$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \\$host;
        proxy_read_timeout 86400;
    }}

    location /healthz {{
        auth_basic off;
        proxy_pass http://127.0.0.1:8501/healthz;
    }}

    location /PORT6080/ {{
        auth_basic off;
        rewrite ^/PORT6080/(.*) /\\$1 break;
        proxy_pass http://127.0.0.1:6080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \\$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \\$host;
        proxy_read_timeout 86400;
    }}

    location /websockify {{
        auth_basic off;
        proxy_pass http://127.0.0.1:6080/websockify;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \\$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \\$host;
        proxy_read_timeout 86400;
    }}
}}
EOFNGINX

ln -sf /etc/nginx/sites-available/computer-use /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
systemctl restart nginx
systemctl enable nginx

echo "✅ DEPLOYMENT COMPLETE!"
IP=\\$(curl -s http://169.254.169.254/hetzner/v1/metadata/public-ipv4)
echo "Access at: http://\\$IP/"
echo "Username: admin"
echo "Password: anthropic2024"
"""

    result = subprocess.run([
        "ssh", "-o", "StrictHostKeyChecking=no",
        f"root@{ip}",
        build_script
    ])

    return result.returncode == 0

def main():
    # Check environment
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    # Get local path
    local_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"Local computer-use-demo path: {local_path}")

    # Create instance
    print("\n=== Creating Hetzner instance ===")
    manager = HetznerManager()

    user_data = generate_minimal_cloud_init(api_key, manager.api_token)
    name = f"local-deploy-{int(time.time())}"

    server = manager.create_instance(
        name=name,
        user_data=user_data,
        labels={"app": "computer-use-demo", "deploy-type": "local"}
    )

    ip = server['public_net']['ipv4']['ip']
    server_id = server['id']

    print(f"✅ Instance created: {name}")
    print(f"   IP: {ip}")
    print(f"   ID: {server_id}")

    # Wait for SSH
    print("\n=== Waiting for SSH access ===")
    if not wait_for_ssh(ip):
        print("❌ SSH timeout - check instance manually")
        sys.exit(1)

    # Upload files
    print("\n=== Uploading local files ===")
    if not upload_local_files(ip, local_path):
        print("❌ Upload failed")
        sys.exit(1)

    # Build and start
    print("\n=== Building and starting services ===")
    if not build_and_start(ip, api_key):
        print("❌ Build/start failed")
        sys.exit(1)

    print("\n" + "="*50)
    print("✅✅✅ LOCAL DEPLOYMENT COMPLETE! ✅✅✅")
    print("="*50)
    print(f"\n🌐 Access at: http://{ip}/")
    print(f"👤 Username: admin")
    print(f"🔑 Password: anthropic2024")
    print("\nAll features from your local files are deployed!")
    print("Chrome should work exactly as it does locally.")

if __name__ == '__main__':
    main()

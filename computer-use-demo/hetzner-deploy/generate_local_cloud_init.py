def generate_local_cloud_init(anthropic_api_key, local_files_b64):
    """Generate cloud-init with embedded local Dockerfile and image/ directory"""
    return f'''#!/bin/bash
set -e
exec > >(tee /var/log/cloud-init-output.log)
exec 2>&1

echo "========== DEPLOYING FROM LOCAL FILES =========="

# Update system
apt-get update && apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh && rm get-docker.sh

# Install tools
apt-get install -y docker-compose-plugin nginx apache2-utils git

# Clone repo for Python code
cd /opt
git clone --depth 1 https://github.com/Consultant-AI/proto-multi.git
cd proto-multi/computer-use-demo

# Replace Dockerfile and image/ with local versions
echo "Extracting local Dockerfile and image/..."
cat > /tmp/local-files.b64 <<'EOFLOCAL'
{local_files_b64}
EOFLOCAL

base64 -d /tmp/local-files.b64 | tar -xzf -
rm /tmp/local-files.b64

# Build Docker image
echo "Building Docker image from LOCAL files..."
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
docker compose up -d
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
    }}

    location /PORT8501/ {{
        auth_basic off;
        rewrite ^/PORT8501/(.*) /$1 break;
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }}

    location /_stcore/ {{
        auth_basic off;
        proxy_pass http://127.0.0.1:8501/_stcore/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
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
        proxy_read_timeout 86400;
    }}

    location /websockify {{
        auth_basic off;
        proxy_pass http://127.0.0.1:6080/websockify;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }}
}}
EOFNGINX

ln -sf /etc/nginx/sites-available/computer-use /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
systemctl restart nginx && systemctl enable nginx

echo "========== LOCAL DEPLOYMENT COMPLETE =========="
IP=$(curl -s http://169.254.169.254/hetzner/v1/metadata/public-ipv4)
echo "✅ Deployed from local Dockerfile and image/"
echo "🌐 http://$IP/"
echo "👤 admin / 🔑 anthropic2024"
'''

# Read the base64 local files
with open('/tmp/local-files.b64') as f:
    local_b64 = f.read().strip()

from hetzner_manager import HetznerManager
import os

manager = HetznerManager()
api_key = os.environ.get('ANTHROPIC_API_KEY')

cloud_init = generate_local_cloud_init(api_key, local_b64)

server = manager.create_instance(
    name=f"local-{int(__import__('time').time())}",
    user_data=cloud_init,
    labels={"app": "computer-use-demo", "source": "local"}
)

print(f"✅ Instance created: {server['name']}")
print(f"   IP: {server['public_net']['ipv4']['ip']}")
print(f"   ID: {server['id']}")
print(f"\n🌐 Will be ready at: http://{server['public_net']['ipv4']['ip']}/")
print(f"👤 admin / 🔑 anthropic2024")
print("\nDeployment uses YOUR LOCAL Dockerfile and image/ files!")

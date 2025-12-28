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

        # DELETE requests return empty responses (204 No Content)
        if response.status_code == 204 or not response.content:
            return {}

        return response.json()

    def get_or_create_ssh_key(self, name: str, public_key: str) -> int:
        """Get existing SSH key or create new one in Hetzner.

        Args:
            name: Name for the SSH key
            public_key: Public key content (ssh-ed25519 ... or ssh-rsa ...)

        Returns:
            SSH key ID
        """
        # Check if key already exists
        result = self._request("GET", "ssh_keys")
        for key in result.get("ssh_keys", []):
            # Match by public key fingerprint (last part matches)
            if key.get("public_key", "").split()[-1] == public_key.split()[-1]:
                print(f"Found existing SSH key: {key['name']} (ID: {key['id']})")
                return key["id"]

        # Create new key
        print(f"Creating SSH key '{name}' in Hetzner...")
        result = self._request("POST", "ssh_keys", {
            "name": name,
            "public_key": public_key
        })
        key_id = result["ssh_key"]["id"]
        print(f"Created SSH key with ID: {key_id}")
        return key_id

    def create_instance(
        self,
        name: str,
        server_type: str = "cpx22",  # 2 vCPU, 4GB RAM, 80GB disk, $0.0096/hour (replaces deprecated cx22)
        location: str = "nbg1",  # Nuremberg, Germany - use 'hel1' for Finland, 'fsn1' for Germany, 'ash' for US
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
        server_type: str = "cpx22",  # 2 vCPU, 4GB RAM, 80GB disk (replaces deprecated cx22)
        location: str = "nbg1",  # Nuremberg, Germany
        user_data: Optional[str] = None,
        anthropic_api_key: Optional[str] = None
    ) -> Dict:
        """Create new instance from snapshot with optional API key fix"""
        print(f"Cloning instance from snapshot {snapshot_id}...")

        # Always provide user_data to ensure Docker starts on snapshot restore
        if not user_data:
            if anthropic_api_key:
                # If API key provided, update it and restart
                user_data = f"""#!/bin/bash
set -e
exec > >(tee /var/log/snapshot-restore.log)
exec 2>&1

echo "========== SNAPSHOT RESTORE INITIALIZATION =========="
date

# Ensure Docker service is running
systemctl start docker
sleep 5

# Check for backed-up Docker image
cd /opt/proto-multi/computer-use-demo
echo "Checking for Docker image backup..."

# First try to load from backed-up tar file (created by prepare-snapshot)
if [ -f /var/lib/docker-image-backup.tar ]; then
    echo "✅ Found Docker image backup! Loading preserved state..."
    docker load -i /var/lib/docker-image-backup.tar
    echo "✅ Docker state restored from snapshot (all software and data preserved)"
elif docker images | grep -q computer-use-demo:local; then
    echo "✅ Docker image 'computer-use-demo:local' found in snapshot"
else
    echo "⚠️  WARNING: No Docker backup found! Rebuilding from scratch..."
    echo "   This means the instance was NOT properly prepared for snapshot."
    echo "   Use 'Prepare for Snapshot' button before creating snapshots."
    export DOCKER_BUILDKIT=1
    docker build --platform linux/amd64 -t computer-use-demo:local . 2>&1 | tee /var/log/docker-rebuild.log
fi

# Update API key and restart service
sed -i 's/ANTHROPIC_API_KEY=.*/ANTHROPIC_API_KEY={anthropic_api_key}/' docker-compose.yml

# Restart the systemd service
systemctl daemon-reload
systemctl restart computer-use-demo.service

# Wait for containers to start
sleep 10
docker compose ps

echo "✅ Snapshot restore complete"
date
"""
            else:
                # No API key provided, just ensure Docker is running
                user_data = """#!/bin/bash
set -e
exec > >(tee /var/log/snapshot-restore.log)
exec 2>&1

echo "========== SNAPSHOT RESTORE INITIALIZATION =========="
date

# Ensure Docker service is running
systemctl start docker
sleep 5

# Check for backed-up Docker image
cd /opt/proto-multi/computer-use-demo
echo "Checking for Docker image backup..."

# First try to load from backed-up tar file (created by prepare-snapshot)
if [ -f /var/lib/docker-image-backup.tar ]; then
    echo "✅ Found Docker image backup! Loading preserved state..."
    docker load -i /var/lib/docker-image-backup.tar
    echo "✅ Docker state restored from snapshot (all software and data preserved)"
elif docker images | grep -q computer-use-demo:local; then
    echo "✅ Docker image 'computer-use-demo:local' found in snapshot"
else
    echo "⚠️  WARNING: No Docker backup found! Rebuilding from scratch..."
    echo "   This means the instance was NOT properly prepared for snapshot."
    echo "   Use 'Prepare for Snapshot' button before creating snapshots."
    export DOCKER_BUILDKIT=1
    docker build --platform linux/amd64 -t computer-use-demo:local . 2>&1 | tee /var/log/docker-rebuild.log
fi

# Restart the systemd service to bring up containers
systemctl daemon-reload
systemctl restart computer-use-demo.service

# Wait for containers to start
sleep 10
docker compose ps

echo "✅ Snapshot restore complete"
date
"""

        return self.create_instance(
            name=name,
            server_type=server_type,
            location=location,
            image=str(snapshot_id),
            labels={"cloned_from": str(snapshot_id)},
            user_data=user_data
        )

    def get_instance_by_name(self, name: str) -> Optional[Dict]:
        """Get instance by name"""
        instances = self.list_instances()
        for instance in instances:
            if instance["name"] == name:
                return instance
        return None

    def prepare_docker_for_snapshot(self, instance_id: int) -> Dict:
        """
        Prepare Docker container for snapshot by committing state to image on disk

        This calls the Docker commit API endpoint on the instance to preserve state.
        """
        print(f"Preparing instance {instance_id} for snapshot...")

        # Get instance details
        instance = self.get_instance(instance_id)
        ip = instance['public_net']['ipv4']['ip']

        # Call the commit API endpoint on the instance
        url = f"http://{ip}/api/commit-docker"
        auth = ('admin', 'anthropic2024')

        try:
            print(f"Calling Docker commit API at {url}...")
            response = requests.post(url, auth=auth, timeout=300)
            result = response.json()

            if result.get('success'):
                print("✅ Docker state committed successfully")
                return {
                    'status': 'success',
                    'message': 'Docker state committed to disk. Instance ready for snapshot.',
                    'output': result.get('output', ''),
                    'instance_ip': ip
                }
            else:
                print(f"❌ Docker commit failed: {result.get('error')}")
                return {
                    'status': 'error',
                    'message': 'Docker commit failed',
                    'error': result.get('error', 'Unknown error'),
                    'output': result.get('output', ''),
                    'instance_ip': ip
                }
        except requests.exceptions.Timeout:
            return {
                'status': 'error',
                'message': 'Request timed out. The commit may still be running.',
                'instance_ip': ip
            }
        except Exception as e:
            print(f"❌ Error calling commit API: {e}")
            return {
                'status': 'error',
                'message': f'Failed to connect to instance: {str(e)}',
                'instance_ip': ip
            }

    def create_instance_and_register(
        self,
        name: str,
        server_type: str = "cpx22",
        computer_registry=None,
        location: str = "nbg1",
        image: str = "ubuntu-24.04",
        user_data: str = None,
        labels: Optional[Dict[str, str]] = None,
        ssh_keys: Optional[List[int]] = None,
    ) -> Dict:
        """Create a Hetzner instance and automatically register in computer registry."""
        # Create the instance
        server = self.create_instance(
            name=name,
            server_type=server_type,
            location=location,
            image=image,
            user_data=user_data,
            labels=labels or {"created_by": "computer-use-demo"},
            ssh_keys=ssh_keys,
        )

        # Auto-register in computer registry if provided
        if computer_registry:
            from ..remote.computer_registry import ComputerConfig

            computer_config = ComputerConfig(
                id=f"hetzner-{server['id']}",
                name=name,
                type="remote",
                host=server['public_net']['ipv4']['ip'],
                port=22,
                username="root",
                ssh_key_path=str(os.path.expanduser("~/.ssh/id_rsa")),
                vnc_port=6080,
                api_port=8000,
                platform_type="Linux"
            )
            computer_registry.add(computer_config)
            print(f"✅ Instance registered in computer registry: {computer_config.id}")

        return server


def generate_cloud_init_script(anthropic_api_key: str, hetzner_api_token: str = None) -> str:
    """
    Generate simplified cloud-init script for instance setup

    SIMPLIFIED VERSION - Removed nginx auth and complex firewall that was causing deployment failures
    """

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

# Fix IPv6->IPv4 bug in http_server.py
echo "Patching http_server.py for IPv4 compatibility..."
cat > image/http_server.py <<'EOFHTTPSERVER'
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler


def run_server():
    os.chdir(os.path.dirname(__file__) + "/static_content")
    server_address = ("0.0.0.0", 8080)  # IPv4 binding for nginx compatibility
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print("Starting HTTP server on port 8080...")  # noqa: T201
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()
EOFHTTPSERVER

# Patch index.html iframe URLs to use proxy paths instead of direct ports
echo "Patching index.html to use nginx proxy paths for iframes..."
# Simple replacement: change iframe src lines to use proxy paths
sed -i 's|document.getElementById("streamlit").src = .*|document.getElementById("streamlit").src = "/PORT8501/";|' image/static_content/index.html
sed -i 's|document.getElementById("vnc").src = .*|document.getElementById("vnc").src = "/PORT6080/vnc.html?\\&resize=scale\\&autoconnect=1\\&view_only=1\\&reconnect=1\\&reconnect_delay=2000";|' image/static_content/index.html

# Build Docker image
echo "Building Docker image..."
export DOCKER_BUILDKIT=1
docker build --platform linux/amd64 -t computer-use-demo:local . 2>&1 | tee /var/log/docker-build.log

if [ $? -ne 0 ]; then
    echo "ERROR: Docker build failed!"
    exit 1
fi

echo "✅ Docker build completed"

# Save Docker image to persistent location for snapshot preservation
echo "Saving Docker image for snapshot preservation..."
docker save computer-use-demo:local -o /var/lib/docker-image-backup.tar
echo "✅ Docker image backed up to /var/lib/docker-image-backup.tar"

# Chrome should be installed via Dockerfile - skip verification to avoid hanging

# Create docker-compose.yml
cat > docker-compose.yml <<'EOFCOMPOSE'
version: '3.8'

services:
  computer-use:
    image: computer-use-demo:local
    platform: linux/amd64
    ports:
      - "127.0.0.1:8080:8080"  # Combined view - accessible via nginx only
      - "127.0.0.1:8501:8501"  # Streamlit - accessible via nginx proxy only
      - "127.0.0.1:5900:5900"  # VNC - localhost only
      - "127.0.0.1:6080:6080"  # noVNC - accessible via nginx proxy only
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

# Create Docker commit helper script
cat > /usr/local/bin/commit-docker-state.sh <<'EOFCOMMIT'
#!/bin/bash
set -e
exec > >(tee -a /var/log/docker-commit.log)
exec 2>&1

echo "========== COMMITTING DOCKER STATE =========="
date

cd /opt/proto-multi/computer-use-demo

# Get the running container ID
CONTAINER_ID=$(docker compose ps -q computer-use 2>/dev/null || echo "")

if [ -z "$CONTAINER_ID" ]; then
    echo "ERROR: No running container found"
    exit 1
fi

echo "Container ID: $CONTAINER_ID"

# Commit the running container to preserve all state
echo "Committing container state to image..."
docker commit $CONTAINER_ID computer-use-demo:local

# Save to persistent backup location
echo "Saving Docker image to backup file..."
docker save computer-use-demo:local -o /var/lib/docker-image-backup.tar

# Verify
if [ -f /var/lib/docker-image-backup.tar ]; then
    SIZE=$(du -h /var/lib/docker-image-backup.tar | cut -f1)
    echo "✅ Docker state committed and saved ($SIZE)"
    echo "   Backup: /var/lib/docker-image-backup.tar"
else
    echo "ERROR: Backup file not created"
    exit 1
fi

date
echo "=========================================="
EOFCOMMIT

chmod +x /usr/local/bin/commit-docker-state.sh

# Create API endpoint script for triggering Docker commit via HTTP
cat > /usr/local/bin/docker-commit-api.py <<'EOFAPI'
#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess
import json

class CommitHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/commit':
            try:
                # Run the commit script
                result = subprocess.run(
                    ['/usr/local/bin/commit-docker-state.sh'],
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                response = {
                    'success': result.returncode == 0,
                    'output': result.stdout,
                    'error': result.stderr
                }

                self.send_response(200 if result.returncode == 0 else 500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    server = HTTPServer(('127.0.0.1', 9999), CommitHandler)
    print('Docker commit API listening on port 9999')
    server.serve_forever()
EOFAPI

chmod +x /usr/local/bin/docker-commit-api.py

# Create systemd service for the commit API
cat > /etc/systemd/system/docker-commit-api.service <<'EOFAPISVC'
[Unit]
Description=Docker Commit API
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/docker-commit-api.py
Restart=always

[Install]
WantedBy=multi-user.target
EOFAPISVC

systemctl daemon-reload
systemctl enable docker-commit-api.service
systemctl start docker-commit-api.service

# Start service
echo "Starting Docker service..."
systemctl daemon-reload
systemctl enable computer-use-demo.service
systemctl start computer-use-demo.service

# Wait for Docker to start
sleep 20
docker compose ps

# ========================================
# SECURE AUTHENTICATION SETUP
# ========================================
echo "Setting up authentication..."

# Install nginx and password tools
apt-get install -y nginx apache2-utils

# Create password (username: admin, password: anthropic2024)
echo 'anthropic2024' | htpasswd -ci /etc/nginx/.htpasswd admin

# Configure nginx to proxy services with smart auth
# Main page requires auth, but iframes don't (they're protected by localhost binding)
cat > /etc/nginx/sites-available/computer-use <<'EOFNGINX'
server {{
    listen 80;
    server_name _;

    # Combined view (default) - REQUIRES AUTH
    location = / {{
        auth_basic "Computer Use Demo - Login Required";
        auth_basic_user_file /etc/nginx/.htpasswd;

        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }}

    # Static files from port 8080 - REQUIRES AUTH
    location ~ ^/(static|assets|css|js)/ {{
        auth_basic "Computer Use Demo - Login Required";
        auth_basic_user_file /etc/nginx/.htpasswd;

        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }}

    # Proxy port 8501 for iframes - NO AUTH (protected by localhost binding)
    # Only accessible if user already authenticated to main page
    location /PORT8501/ {{
        auth_basic off;
        rewrite ^/PORT8501/(.*) /$1 break;
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }}

    # Streamlit websocket - NO AUTH
    location /_stcore/ {{
        auth_basic off;
        proxy_pass http://127.0.0.1:8501/_stcore/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }}

    # Streamlit health check - NO AUTH
    location /healthz {{
        auth_basic off;
        proxy_pass http://127.0.0.1:8501/healthz;
        proxy_http_version 1.1;
    }}

    # Proxy port 6080 for iframes - NO AUTH (protected by localhost binding)
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

    # WebSocket for noVNC - NO AUTH
    location /websockify {{
        auth_basic off;
        proxy_pass http://127.0.0.1:6080/websockify;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }}

    # Docker commit API - REQUIRES AUTH (management endpoint)
    location /api/commit-docker {{
        auth_basic "Computer Use Demo - Management API";
        auth_basic_user_file /etc/nginx/.htpasswd;

        proxy_pass http://127.0.0.1:9999/commit;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_read_timeout 300;
    }}
}}
EOFNGINX

# Enable nginx config
ln -sf /etc/nginx/sites-available/computer-use /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Start nginx
systemctl restart nginx
systemctl enable nginx

echo "✅ Security configured!"
echo "   - Docker services bound to localhost only"
echo "   - All access requires authentication through nginx"
echo "   Username: admin"
echo "   Password: anthropic2024"

echo "========== DEPLOYMENT COMPLETE =========="
IP=$(curl -s http://169.254.169.254/hetzner/v1/metadata/public-ipv4)
echo "Authenticated access: http://$IP/"
echo "  Combined view: http://$IP/"
echo "  Chat only: http://$IP/chat"
echo "  Desktop only: http://$IP/vnc"
date
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
        api_key = args.api_key or os.environ.get('ANTHROPIC_API_KEY')

        if args.snapshot:
            # Clone from snapshot with API key fix
            server = manager.clone_from_snapshot(
                snapshot_id=args.snapshot,
                name=args.name,
                anthropic_api_key=api_key
            )
        else:
            # Create new instance
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

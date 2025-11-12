# Developer Guide: Hetzner Computer Use Demo Deployment System

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Code Structure](#code-structure)
4. [Deployment Methods](#deployment-methods)
5. [Dashboard Usage](#dashboard-usage)
6. [API Reference](#api-reference)
7. [Security Features](#security-features)
8. [Troubleshooting](#troubleshooting)

---

## Overview

This deployment system allows you to create, manage, and monitor secure Hetzner cloud instances running the Anthropic Computer Use Demo. Each instance provides:

- **Streamlit Chat Interface** - Interact with Claude
- **VNC Desktop Environment** - Full Ubuntu desktop with Chrome, VSCode, LibreOffice
- **Authentication** - Password-protected access (admin/anthropic2024)
- **Security** - All services bound to localhost, accessible only via nginx proxy

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Local Machine                            │
│  ┌──────────────────┐         ┌────────────────────┐       │
│  │  Dashboard       │         │  Local Files       │       │
│  │  (Port 5500)     │────────▶│  - Dockerfile      │       │
│  │  - Flask App     │         │  - image/          │       │
│  │  - Control Panel │         │  - computer_use_   │       │
│  └──────────────────┘         └────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
                    │
                    │ Hetzner API
                    ▼
┌─────────────────────────────────────────────────────────────┐
│                  Hetzner Cloud Instances                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Nginx (Port 80) - Password Auth                       │ │
│  │  ├─ / → localhost:8080 (Combined View)                 │ │
│  │  ├─ /PORT8501/ → localhost:8501 (Streamlit Proxy)      │ │
│  │  └─ /PORT6080/ → localhost:6080 (VNC Proxy)            │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Docker Container (Bound to localhost only)            │ │
│  │  ├─ Port 8080: Combined View (Chat + VNC iframes)      │ │
│  │  ├─ Port 8501: Streamlit Chat Interface                │ │
│  │  ├─ Port 5900: VNC Server                              │ │
│  │  └─ Port 6080: noVNC Web Interface                     │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Security Model

**Two-Layer Security:**
1. **Nginx Authentication** - Port 80 requires username/password
2. **Localhost Binding** - Direct port access blocked from internet

```
Internet User
    │
    │ (Try to access port 8501 directly)
    ▼
  BLOCKED ❌  (Bound to 127.0.0.1)

Internet User
    │
    │ (Access port 80 with credentials)
    ▼
  Nginx Auth Check
    │
    ├─ No credentials → 401 Unauthorized ❌
    └─ Valid credentials → Proxy to localhost services ✅
```

---

## Code Structure

### Directory Layout

```
computer-use-demo/
├── Dockerfile                   # Docker image definition
├── image/                       # Files copied into Docker image
│   ├── .config/
│   │   └── tint2/
│   │       ├── applications/   # Desktop launcher files
│   │       │   ├── chrome.desktop
│   │       │   ├── vscode.desktop
│   │       │   └── ...
│   │       └── tint2rc         # Taskbar configuration
│   ├── static_content/
│   │   └── index.html          # Combined view (iframes)
│   ├── entrypoint.sh           # Container startup script
│   ├── http_server.py          # Serves index.html on port 8080
│   ├── start_all.sh            # Starts X, VNC, desktop
│   └── ...
├── computer_use_demo/          # Python application
│   ├── streamlit.py            # Main Streamlit app
│   ├── loop.py                 # Claude interaction loop
│   └── requirements.txt
└── hetzner-deploy/             # Deployment scripts
    ├── hetzner_manager.py      # Core deployment logic
    ├── control_panel.py        # Dashboard web interface
    ├── generate_local_cloud_init.py  # Local file deployment
    └── requirements.txt
```

### Key Files Explained

#### `hetzner_manager.py`
Core deployment manager that handles:
- Hetzner API communication
- Instance creation/deletion
- Cloud-init script generation
- Snapshot management

```python
class HetznerManager:
    def create_instance(name, user_data, labels)  # Create new instance
    def delete_instance(instance_id)              # Delete instance
    def list_instances(label_selector)            # List all instances
    def start_instance(instance_id)               # Start stopped instance
    def stop_instance(instance_id)                # Stop running instance
    def create_snapshot(instance_id, desc)        # Create snapshot
```

#### `control_panel.py`
Flask web dashboard for managing instances:
- Authentication: HTTP Basic Auth (admin/anthropic2024)
- REST API for instance management
- Web UI for visual control

```python
@app.route('/api/instances')                    # List instances
@app.route('/api/instance/create')              # Create instance
@app.route('/api/instance/<id>/start')          # Start instance
@app.route('/api/instance/<id>/stop')           # Stop instance
@app.route('/api/instance/<id>/delete')         # Delete instance
@app.route('/api/instance/<id>/snapshot')       # Create snapshot
@app.route('/api/snapshots')                    # List snapshots
@app.route('/api/snapshot/<id>/delete')         # Delete snapshot
```

#### `generate_local_cloud_init.py`
Deployment script that embeds local files:
- Creates tarball of local Dockerfile and image/
- Base64 encodes for cloud-init embedding
- Deploys using YOUR local files instead of GitHub

#### `index.html`
Combined view that loads both Streamlit and VNC:
- Auto-detects if accessed via port 80 (nginx) or 8080 (direct)
- Uses proxy paths (`/PORT8501/`, `/PORT6080/`) when on port 80
- Uses direct ports when accessed directly

---

## Deployment Methods

### Method 1: Dashboard (Recommended)

**Start the Dashboard:**
```bash
cd computer-use-demo/hetzner-deploy
export HETZNER_API_TOKEN=your-token
export ANTHROPIC_API_KEY=your-key
python3 control_panel.py
```

Access at: http://localhost:5500
- Username: `admin`
- Password: `anthropic2024`

**Features:**
- Visual interface for all operations
- Create instances with one click
- Pause/resume instances
- Create snapshots
- Monitor status in real-time

### Method 2: Local File Deployment (For Custom Code)

**Use this when you have local changes to Dockerfile or image/ directory:**

```bash
cd computer-use-demo/hetzner-deploy
export HETZNER_API_TOKEN=your-token
export ANTHROPIC_API_KEY=your-key
python3 generate_local_cloud_init.py
```

**What it does:**
1. Creates tarball of your local Dockerfile and image/
2. Base64 encodes it (fits in cloud-init 32KB limit)
3. Embeds in cloud-init script
4. Deploys to Hetzner
5. Extracts and builds from YOUR local files

**When to use:**
- Testing Chrome fixes locally
- Custom desktop applications
- Modified Docker configuration
- Local-only changes not in GitHub

### Method 3: Command Line (For Scripts)

```bash
cd computer-use-demo/hetzner-deploy
export HETZNER_API_TOKEN=your-token
export ANTHROPIC_API_KEY=your-key

# Create instance
python3 hetzner_manager.py create --name "my-instance" --api-key "$ANTHROPIC_API_KEY"

# List instances
python3 hetzner_manager.py list

# Delete instance
python3 hetzner_manager.py delete <instance-id>
```

---

## Dashboard Usage

### Accessing the Dashboard

1. **Start Dashboard:**
```bash
export HETZNER_API_TOKEN=your-token
export ANTHROPIC_API_KEY=your-key
python3 control_panel.py
```

2. **Open Browser:**
- URL: http://localhost:5500
- Username: `admin`
- Password: `anthropic2024`

### Dashboard Features

#### 1. Create New Instance

**Fresh Instance:**
- Click "Create Instance" button
- Enter instance name
- Leave "From Snapshot" empty
- Click "Create"
- Wait 10-12 minutes for deployment

**From Snapshot:**
- Click "Create Instance" button
- Enter instance name
- Select snapshot from dropdown
- Click "Create"
- Wait 2-3 minutes for deployment

#### 2. Pause/Resume Instance

**Pause (Stop):**
- Click "Pause" button on running instance
- Saves state but stops billing compute time
- Storage still billed (~€0.01/month per GB)

**Resume (Start):**
- Click "Start" button on stopped instance
- Restores to previous state
- Takes 1-2 minutes

**Use Cases:**
- Save costs when not using instance
- Preserve configuration without snapshots
- Quick on/off for testing

#### 3. Create Snapshot

**Purpose:**
- Save complete instance state
- Clone instances with identical configuration
- Backup before major changes

**How to:**
- Click "Snapshot" button on any instance
- Enter description (e.g., "chrome-working-2025-11-02")
- Wait 3-5 minutes for snapshot creation
- Snapshot appears in "Snapshots" section

**Cost:**
- ~€0.01 per GB per month
- Typical snapshot: 2.5GB = €0.025/month

#### 4. Delete Instance

- Click "Delete" button
- Confirms before deletion
- Permanent - cannot be undone
- Stops all billing for that instance

#### 5. Delete Snapshot

- Scroll to "Snapshots" section
- Click "Delete" on snapshot
- Stops storage billing

### Instance Status

**Status Indicators:**
- **Green "RUNNING"** - Instance is up and accessible
- **Services Ready: Yes** - Port 80 responding (services running)
- **Services Ready: No** - Still deploying or services failed

**Accessing Instances:**
- Click on IP address to open in new tab
- Login with `admin` / `anthropic2024`
- See combined view with Streamlit + VNC

---

## API Reference

All API endpoints require HTTP Basic Authentication (`admin` / `anthropic2024`).

### List Instances
```bash
curl -u admin:anthropic2024 http://localhost:5500/api/instances
```

**Response:**
```json
{
  "instances": [
    {
      "id": 112056900,
      "name": "local-1762088957",
      "status": "running",
      "services_ready": true,
      "ip": "46.224.25.228",
      "created": "2025-11-02T13:09:18Z",
      "server_type": "cx22",
      "cost_per_hour": 0.007,
      "urls": {
        "chat": "http://46.224.25.228/",
        "desktop": "http://46.224.25.228/"
      }
    }
  ]
}
```

### Create Instance
```bash
curl -u admin:anthropic2024 \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"name": "test-instance"}' \
  http://localhost:5500/api/instance/create
```

**Create from Snapshot:**
```bash
curl -u admin:anthropic2024 \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"name": "cloned-instance", "snapshot_id": 329745509}' \
  http://localhost:5500/api/instance/create
```

### Start Instance
```bash
curl -u admin:anthropic2024 \
  -X POST \
  http://localhost:5500/api/instance/112056900/start
```

### Stop Instance
```bash
curl -u admin:anthropic2024 \
  -X POST \
  http://localhost:5500/api/instance/112056900/stop
```

### Delete Instance
```bash
curl -u admin:anthropic2024 \
  -X DELETE \
  http://localhost:5500/api/instance/112056900/delete
```

### Create Snapshot
```bash
curl -u admin:anthropic2024 \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"description": "my-snapshot"}' \
  http://localhost:5500/api/instance/112056900/snapshot
```

### List Snapshots
```bash
curl -u admin:anthropic2024 http://localhost:5500/api/snapshots
```

### Delete Snapshot
```bash
curl -u admin:anthropic2024 \
  -X DELETE \
  http://localhost:5500/api/snapshot/329745509/delete
```

---

## Security Features

### Authentication System

**Local Dashboard:**
- HTTP Basic Auth on port 5500
- Username: `admin`
- Password: `anthropic2024`
- Protects all API endpoints

**Remote Instances:**
- HTTP Basic Auth on port 80
- Username: `admin`
- Password: `anthropic2024`
- Required for all access

**Password File:**
```bash
# Generated in cloud-init
echo 'anthropic2024' | htpasswd -ci /etc/nginx/.htpasswd admin
```

### Port Security

**Blocked Ports (Not accessible from internet):**
- 8080 - Combined view
- 8501 - Streamlit
- 5900 - VNC
- 6080 - noVNC

**Open Ports:**
- 80 - Nginx with authentication

**Docker Compose Configuration:**
```yaml
ports:
  - "127.0.0.1:8080:8080"  # Localhost only
  - "127.0.0.1:8501:8501"  # Localhost only
  - "127.0.0.1:5900:5900"  # Localhost only
  - "127.0.0.1:6080:6080"  # Localhost only
```

### Nginx Configuration

```nginx
server {
    listen 80;

    # Main page - requires auth
    location = / {
        auth_basic "Computer Use Demo";
        auth_basic_user_file /etc/nginx/.htpasswd;
        proxy_pass http://127.0.0.1:8080;
    }

    # Iframe proxies - no auth (protected by localhost binding)
    location /PORT8501/ {
        auth_basic off;  # No separate auth for iframes
        proxy_pass http://127.0.0.1:8501;
    }

    location /PORT6080/ {
        auth_basic off;
        proxy_pass http://127.0.0.1:6080;
    }
}
```

**Security Model:**
1. User authenticates on main page (port 80)
2. Browser receives HTML with iframes pointing to proxy paths
3. Iframes load without separate auth (same session)
4. Direct port access blocked by localhost binding

---

## Troubleshooting

### Dashboard Issues

**Problem: Dashboard won't start**
```bash
# Check if port 5500 is already in use
lsof -ti:5500

# Kill existing process
lsof -ti:5500 | xargs kill -9

# Restart dashboard
python3 control_panel.py
```

**Problem: "services_ready" shows false**
- This means port 80 isn't responding yet
- Wait 10-12 minutes for fresh deployments
- Wait 2-3 minutes for snapshot deployments
- If stuck, check instance logs (requires SSH)

**Problem: Can't authenticate to dashboard**
- Username: `admin` (lowercase)
- Password: `anthropic2024`
- Check browser isn't caching old credentials

### Deployment Issues

**Problem: Deployment takes >15 minutes**
- Docker build may be slow
- Check Hetzner status page
- Delete and recreate instance

**Problem: Instance created but not accessible**
```bash
# Check if instance is running
python3 hetzner_manager.py list

# Wait for cloud-init to complete (10-12 minutes)
# Check port 80
curl -I http://<instance-ip>/
```

**Problem: Iframes not loading**
- Verify you're accessing via port 80 (not 8080)
- Check browser console for errors
- Ensure nginx is running on instance
- Verify proxy paths are configured

**Problem: Chrome not launching**
- This was fixed by deploying from local files
- Use `generate_local_cloud_init.py` for deployment
- Verify Chrome desktop file exists in image/.config/tint2/applications/

### Instance Access Issues

**Problem: 401 Unauthorized**
- Username: `admin`
- Password: `anthropic2024`
- Clear browser cache/cookies

**Problem: Connection refused**
- Instance still deploying (wait 10-12 minutes)
- Instance stopped (click "Start" in dashboard)
- Firewall blocking port 80 (check Hetzner firewall)

**Problem: Blank page after login**
- Docker services not started yet
- Wait 2-3 more minutes
- Check if port 8080 is running inside container

### Cost Management

**Typical Costs (CX22 instance):**
- Running instance: €0.007/hour = €5.04/month
- Stopped instance: €0 compute + storage (~€0.30/month)
- Snapshot: ~€0.025/month (for 2.5GB)

**Best Practices:**
1. **Stop instances** when not in use (saves compute costs)
2. **Delete old snapshots** to save storage costs
3. **Delete unused instances** completely
4. **Use snapshots** to clone working configurations

**Check Current Usage:**
```bash
curl -u admin:anthropic2024 http://localhost:5500/api/instances
# Count running instances
# Calculate: count × €0.007/hour
```

---

## Development Workflow

### Making Changes to Local Code

**1. Modify Local Files:**
```bash
cd computer-use-demo
# Edit Dockerfile, image/, or computer_use_demo/
```

**2. Deploy with Local Changes:**
```bash
cd hetzner-deploy
python3 generate_local_cloud_init.py
```

**3. Test on Instance:**
- Wait for deployment (10-12 minutes)
- Access at http://<ip>/
- Test changes

**4. If Changes Work, Update GitHub:**
```bash
git add .
git commit -m "Description of changes"
git push
```

### Adding Desktop Applications

**1. Add Desktop File:**
```bash
# Create file: image/.config/tint2/applications/myapp.desktop
[Desktop Entry]
Name=My App
Exec=/usr/bin/myapp --flags
Icon=myapp
Terminal=false
Type=Application
```

**2. Install Application in Dockerfile:**
```dockerfile
RUN apt-get install -y myapp
```

**3. Add to Taskbar:**
Edit `image/.config/tint2/tint2rc`:
```
launcher_item_app = /home/computeruse/.config/tint2/applications/myapp.desktop
```

**4. Deploy:**
```bash
python3 generate_local_cloud_init.py
```

### Customizing Authentication

**Change Password:**

Edit `generate_local_cloud_init.py` or `hetzner_manager.py`:
```python
# Change this line
echo 'anthropic2024' | htpasswd -ci /etc/nginx/.htpasswd admin

# To
echo 'new-password' | htpasswd -ci /etc/nginx/.htpasswd admin
```

**Change Username:**
```python
# Change both lines
echo 'password' | htpasswd -ci /etc/nginx/.htpasswd newuser
```

Also update `control_panel.py`:
```python
users = {
    "newuser": generate_password_hash("password")
}
```

---

## Advanced Topics

### Creating Custom Snapshots

**Workflow for "Golden Image":**

1. Create fresh instance
2. Customize (install apps, configure settings)
3. Create snapshot
4. Use snapshot to clone instances quickly

**Example:**
```bash
# 1. Create and customize instance
curl -u admin:anthropic2024 -X POST \
  -d '{"name":"golden-image"}' \
  http://localhost:5500/api/instance/create

# 2. Wait for deployment, then customize...

# 3. Create snapshot
curl -u admin:anthropic2024 -X POST \
  -d '{"description":"golden-image-v1"}' \
  http://localhost:5500/api/instance/112056900/snapshot

# 4. Clone from snapshot
curl -u admin:anthropic2024 -X POST \
  -d '{"name":"clone-1", "snapshot_id":329745509}' \
  http://localhost:5500/api/instance/create
```

### Monitoring and Logs

**Dashboard Logs:**
```bash
tail -f /tmp/dashboard.log
```

**Instance Logs (requires SSH):**
```bash
ssh root@<instance-ip>
tail -f /var/log/cloud-init-output.log  # Deployment log
tail -f /var/log/docker-build.log       # Docker build log
docker logs <container-id>              # Container logs
```

### Scaling

**Running Multiple Instances:**
- Each instance runs independently
- Use dashboard to manage all instances
- Share snapshots between instances
- Hetzner limits: 25 servers per project (default)

**Load Considerations:**
- Each CX22 instance: 2 vCPUs, 4GB RAM
- Suitable for 1-2 concurrent Claude sessions
- For more load, use larger instance types

---

## Quick Reference

### Environment Variables
```bash
export HETZNER_API_TOKEN=your-token      # Required for all operations
export ANTHROPIC_API_KEY=your-key        # Required for instance creation
```

### Common Commands
```bash
# Start dashboard
python3 control_panel.py

# Deploy from local files
python3 generate_local_cloud_init.py

# List instances
python3 hetzner_manager.py list

# Delete instance
python3 hetzner_manager.py delete <id>
```

### Important Files
```
hetzner_manager.py          # Core deployment logic
control_panel.py            # Dashboard server
generate_local_cloud_init.py # Local file deployment
image/http_server.py        # Port 8080 HTTP server
image/static_content/index.html  # Combined view HTML
```

### Default Credentials
- **Dashboard:** admin / anthropic2024
- **Instances:** admin / anthropic2024

### Important Ports
- **5500** - Dashboard (local)
- **80** - Instance nginx (remote)
- **8080** - Combined view (localhost only)
- **8501** - Streamlit (localhost only)
- **6080** - noVNC (localhost only)

---

## Support and Contributing

For issues or questions:
1. Check this developer guide
2. Review troubleshooting section
3. Check dashboard logs: `/tmp/dashboard.log`
4. Review instance cloud-init logs (requires SSH access)

When reporting issues, include:
- Dashboard version/commit
- Instance deployment method used
- Full error messages
- Steps to reproduce

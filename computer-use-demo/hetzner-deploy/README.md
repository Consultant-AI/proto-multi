# Hetzner Cloud Deployment for Computer Use Demo

Deploy the Anthropic Computer Use Demo to Hetzner Cloud with:
- ✅ **Fast x86_64 VMs** - Chrome runs natively (no emulation crashes)
- ✅ **Super cheap** - €4.49/month (~$5), pay only when running
- ✅ **One-click deploy** - Launch instances in 30 seconds
- ✅ **Snapshot & clone** - Save your setup and replicate it
- ✅ **AI-spawned instances** - Chat can create new instances for subtasks

## Quick Start

### 1. Get API Tokens

**Hetzner API Token:**
1. Go to https://console.hetzner.cloud/
2. Create account or login
3. Create a new project
4. Go to "Security" → "API Tokens"
5. Generate new token with Read & Write permissions

**Anthropic API Key:**
1. Go to https://console.anthropic.com/
2. Get your API key

### 2. Set Environment Variables

```bash
export HETZNER_API_TOKEN=your-hetzner-token-here
export ANTHROPIC_API_KEY=your-anthropic-key-here
```

### 3. Deploy Your First Instance

```bash
cd hetzner-deploy
chmod +x deploy.sh manage.sh
./deploy.sh
```

**Output:**
```
✅ Instance created: computer-use-1735...
   IP: 123.45.67.89
   ID: 12345678

🌐 Access your instance:
   Chat: http://123.45.67.89:8501
   Chrome: http://123.45.67.89:8080
```

Wait 2-3 minutes for Docker containers to start, then open the URLs!

## Usage

### Deploy New Instance

```bash
# Fresh instance
./deploy.sh

# Custom name
./deploy.sh --name my-dev-instance

# Clone from snapshot
./deploy.sh --name my-clone --snapshot 67890
```

### Manage Instances

```bash
# List all instances
./manage.sh list
# Output: ID    Name              Status    IP
#         12345 computer-use-123  running   123.45.67.89

# Stop instance (pause billing)
./manage.sh stop 12345

# Start instance
./manage.sh start 12345

# Delete instance
./manage.sh delete 12345
```

### Snapshot & Clone

```bash
# Create snapshot (backup your setup)
./manage.sh snapshot 12345 "with-chrome-extensions-installed"

# List snapshots
./manage.sh list-snapshots
# Output: ID    Description                      Created
#         67890 with-chrome-extensions-installed 2025-01-28T...

# Clone from snapshot
./manage.sh clone 67890 my-new-instance
```

**Use Cases:**
- Install Chrome extensions, save snapshot, clone for team
- Configure development environment, clone for each project
- Test different setups without affecting production

## Advanced: AI-Spawned Instances

Enable Claude to spawn new instances for complex subtasks.

### 1. Start Instance Spawner API

On your control machine (or a dedicated small VM):

```bash
cd hetzner-deploy
pip3 install flask requests
python3 instance_spawner.py api
# Runs on http://0.0.0.0:5000
```

### 2. Configure Chat to Use Spawner

Add to your instance environment (in cloud-init or docker-compose):

```yaml
environment:
  - INSTANCE_SPAWNER_API=http://your-control-server-ip:5000
  - HETZNER_INSTANCE_ID=12345  # Current instance ID
```

### 3. Integrate Spawn Tool (Optional)

To fully integrate the spawn tool into Claude's capabilities:

1. Copy `spawn_instance_tool.py` to `computer_use_demo/tools/`
2. Add to `computer_use_demo/tools/__init__.py`:

```python
from .spawn_instance_tool import SpawnInstanceTool

TOOL_GROUPS_BY_VERSION = {
    ToolVersion.V1: ToolGroup(
        tools=[
            BashTool,
            ComputerTool,
            EditTool,
            SpawnInstanceTool,  # Add this
        ],
        ...
    ),
}
```

Now Claude can spawn instances like this:

```
User: "Research the top 10 Python web frameworks and create comparison reports"

Claude: "This is a complex task. Let me spawn separate instances for parallel research..."
[Spawns 3 instances, each researching different frameworks]
```

## Cost Breakdown

### Instance Costs (CX22: 2 vCPU, 4GB RAM)

- **Hourly**: €0.007/hour (~$0.0077/hr)
- **Monthly (24/7)**: €4.49/month (~$5/mo)

**Real Usage Examples:**

| Usage Pattern | Monthly Cost |
|---------------|--------------|
| 8 hours/day, 5 days/week | ~€1.10 (~$1.20) |
| 8 hours/day, 7 days/week | ~€1.68 (~$1.85) |
| 24/7 running | ~€4.49 (~$5.00) |
| Stopped (preserved) | ~€0.01 (IP reservation) |

### Storage Costs

- **Volume**: €0.0476/GB/month (~€1.90 for 40GB)
- **Snapshot**: €0.0119/GB/month (~€0.50 for 40GB snapshot)

**Total for 1 Instance (8hr/day):**
- Running costs: ~€1.68
- Volume: ~€1.90
- Snapshot: ~€0.50
- **Total: ~€4.08/month (~$4.50)**

### Comparison to AWS

Same specs (2 vCPU, 4GB RAM):
- **Hetzner**: €4.49/month ($5)
- **AWS EC2 t3.medium**: ~$35/month
- **Savings**: 87% cheaper

## Architecture

```
Hetzner CX22 Instance (€4.49/month)
├── Ubuntu 24.04 (x86_64)
├── Docker
│   ├── Computer Use Demo Container
│   │   ├── Port 8080: noVNC (Chrome desktop viewer)
│   │   ├── Port 8501: Streamlit chat interface
│   │   └── Port 5900: VNC
│   └── Persistent Volume: /home/computeruse
└── Public IPv4

Optional: Control Server
└── Instance Spawner API (Port 5000)
    └── Manages multi-instance deployments
```

## Workflow Examples

### Example 1: Personal Development

```bash
# Create dev instance
./deploy.sh --name my-dev

# Install tools, extensions, configure Chrome...
# (do this via the web interface)

# Save configuration
./manage.sh snapshot <instance-id> "my-dev-setup"

# Stop instance when not working
./manage.sh stop <instance-id>

# Next day: start instance
./manage.sh start <instance-id>

# Cost: ~€2-3/month for part-time use
```

### Example 2: Team Deployment

```bash
# Manager creates template
./deploy.sh --name template-instance
# Configure with team tools, Chrome signed in to shared account, etc.

# Create snapshot
./manage.sh snapshot <template-id> "team-template-2025-01"

# Team members clone
./manage.sh clone <snapshot-id> alice-workspace
./manage.sh clone <snapshot-id> bob-workspace
./manage.sh clone <snapshot-id> carol-workspace

# Each person has identical setup, works independently
# Cost: €5/month per active member
```

### Example 3: Multi-Task AI Agent

```bash
# Start spawner API
python3 instance_spawner.py api &

# Deploy main instance with spawner enabled
# Claude can now spawn helper instances for:
# - Parallel research tasks
# - Isolated testing environments
# - Long-running background jobs

# Instances auto-spawn and auto-cleanup
# Cost: Pay only for actual usage time
```

## Troubleshooting

### Instance not accessible after creation

Wait 2-3 minutes for Docker containers to fully start. Check with:

```bash
# SSH into instance (add your SSH key in Hetzner console first)
ssh root@<instance-ip>
docker ps
docker logs <container-id>
```

### API token issues

Make sure your token has Read & Write permissions:
```bash
echo $HETZNER_API_TOKEN  # Should show your token
```

### Python dependencies

```bash
pip3 install requests flask
```

## Files

- `hetzner_manager.py` - Core Hetzner API wrapper
- `instance_spawner.py` - Multi-instance orchestration
- `spawn_instance_tool.py` - Claude tool integration
- `deploy.sh` - Quick deployment script
- `manage.sh` - Instance management script

## Security Notes

- Instances are publicly accessible on their IP
- No authentication by default on ports 8080/8501
- For production, add:
  - Firewall rules (Hetzner Cloud Firewall)
  - Authentication proxy (nginx + basic auth)
  - VPN or SSH tunneling

## Next Steps

1. **Deploy your first instance** with `./deploy.sh`
2. **Configure Chrome** with your extensions/settings
3. **Create snapshot** to preserve setup
4. **Stop instance** when not in use to save money
5. **Clone snapshot** when you need more instances

## Support

- Hetzner Docs: https://docs.hetzner.com/cloud/
- Computer Use Demo: https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo
- Issues: Report in the main repository

---

**Enjoy your super-cheap, fast Chrome environment in the cloud!** 🚀

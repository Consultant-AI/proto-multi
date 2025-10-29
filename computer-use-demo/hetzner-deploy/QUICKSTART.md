# Quick Start Guide - 5 Minutes to Deployment

## Prerequisites

1. **Hetzner Account** - Sign up at https://console.hetzner.cloud/ (free)
2. **Anthropic API Key** - Get from https://console.anthropic.com/

## Step 1: Get Hetzner API Token (2 minutes)

1. Login to https://console.hetzner.cloud/
2. Create a new project (or use existing)
3. Click "Security" in left sidebar
4. Click "API Tokens"
5. Click "Generate API Token"
   - Description: "computer-use-demo"
   - Permissions: **Read & Write**
6. Copy the token (you'll only see it once!)

## Step 2: Set Environment Variables

```bash
# Add these to your ~/.bashrc or ~/.zshrc for persistence
export HETZNER_API_TOKEN=your-token-here
export ANTHROPIC_API_KEY=your-anthropic-key-here

# Or just run them in your current terminal
```

## Step 3: Deploy (1 minute)

```bash
cd computer-use-demo/hetzner-deploy

# Install dependencies
pip3 install -r requirements.txt

# Deploy
./deploy.sh
```

**Expected output:**
```
===================================
Hetzner Cloud Computer Use Deploy
===================================

Creating instance 'computer-use-1735...'...
Waiting for instance to start...
✅ Instance created: computer-use-1735...
   IP: 123.45.67.89
   ID: 12345678

🌐 Access your instance:
   Chat: http://123.45.67.89:8501
   Chrome: http://123.45.67.89:8080

✅ Deployment complete!

Wait 2-3 minutes for Docker containers to start, then access:
```

## Step 4: Access Your Instance (2 minutes wait)

1. **Wait 2-3 minutes** for Docker to pull images and start
2. Open `http://<your-ip>:8501` for the **chat interface**
3. Open `http://<your-ip>:8080` for the **Chrome desktop viewer**

You're done! 🎉

## What You Just Created

- **Server**: Hetzner CX22 (2 vCPU, 4GB RAM, x86_64)
- **Cost**: €4.49/month (~$5) if running 24/7
- **Location**: Ashburn, VA (USA) - change with `--location nbg1` for Germany
- **Software**: Ubuntu 24.04 + Docker + Computer Use Demo + Chrome

## Next Steps

### Save Your Setup

After customizing Chrome (installing extensions, signing in, etc.):

```bash
# Create snapshot
./manage.sh snapshot <instance-id> "my-custom-setup"

# List snapshots
./manage.sh list-snapshots
```

### Clone Your Setup

```bash
# Create new instance from snapshot
./manage.sh clone <snapshot-id> my-new-instance
```

### Save Money

```bash
# Stop instance when not in use (stops billing)
./manage.sh stop <instance-id>

# Start when needed
./manage.sh start <instance-id>
```

### Common Commands

```bash
# List all instances
./manage.sh list

# List snapshots
./manage.sh list-snapshots

# Delete instance
./manage.sh delete <instance-id>
```

## Troubleshooting

### "Cannot connect to http://IP:8501"

**Wait longer** - Docker needs 2-3 minutes to:
1. Pull images (~1GB)
2. Start containers
3. Initialize services

Check status by SSH:
```bash
ssh root@<your-ip>
docker ps  # Should show running container
```

### "HETZNER_API_TOKEN not set"

```bash
echo $HETZNER_API_TOKEN  # Should show your token

# If empty:
export HETZNER_API_TOKEN=your-token-here
```

### "requests module not found"

```bash
pip3 install requests
# or
pip3 install -r requirements.txt
```

## Cost Calculator

| Usage Pattern | Monthly Cost |
|---------------|--------------|
| 1 hour/day | ~€0.21 (~$0.23) |
| 4 hours/day | ~€0.84 (~$0.92) |
| 8 hours/day | ~€1.68 (~$1.85) |
| 24/7 | ~€4.49 (~$5.00) |

Plus:
- Persistent storage: ~€1.90/month (40GB volume)
- Snapshot: ~€0.50/month (optional, for backups)

**Total for casual use (8hr/day): ~$4.50/month**

Compare to AWS t3.medium: ~$35/month (7-8x more expensive!)

## Advanced Usage

See [README.md](README.md) for:
- AI-spawned instances for subtasks
- Team deployments
- Multi-instance orchestration
- Security hardening

---

**Questions?** Check the full [README.md](README.md) or open an issue.

# Hetzner Cloud Deployment for Computer Use Demo

## ⚠️ CRITICAL: Why We Use Our Custom Build

**DO NOT use the official `ghcr.io/anthropics/anthropic-quickstarts` Docker image!**

### The Problem with Official Image

The official Anthropic image has a bug in `/static_content/index.html`:

```javascript
// BROKEN (official image)
document.getElementById("streamlit").src = "http://localhost:8501";
document.getElementById("vnc").src = "http://localhost:6080/vnc.html...";
```

This causes **"localhost refused to connect"** errors when accessing port 8080 remotely.

### Our Fix

Our fork at `Consultant-AI/proto-multi` has the corrected version:

```javascript
// FIXED (our custom build)
var hostname = window.location.hostname;  // Gets actual server IP
document.getElementById("streamlit").src = "http://" + hostname + ":8501";
document.getElementById("vnc").src = "http://" + hostname + ":6080/vnc.html...";
```

### Location of Fix

**File:** `computer-use-demo/image/static_content/index.html`
**Lines:** 55-60

### Build Time

- **First build:** 15-20 minutes (must compile Chrome, build Docker image)
- **From snapshot:** 2-3 minutes (recommended approach)

### Recommended Workflow

1. **First time:** Build once (15-20 min), create snapshot immediately
2. **Future instances:** Clone from snapshot (2-3 min)
3. **Cost:** €0.01/GB/month to keep snapshot (~€0.40/month for 40GB)

## Usage

### Start Control Panel

```bash
export HETZNER_API_TOKEN=your-token
export ANTHROPIC_API_KEY=your-key
python3 control_panel.py
```

Open http://localhost:5500

## Features

✅ **Fixed port 8080** - Works correctly when accessed remotely
✅ **Health checks** - Dashboard shows actual service status  
✅ **Auto-start on boot** - Systemd service restarts containers
✅ **Works after pause/resume** - Services auto-start in 1-2 minutes
✅ **Cost optimized** - €0.007/hr running, €0/hr when paused
✅ **Automatic snapshots** - Daily backups, keeps last 7 days

## DO NOT MODIFY

**Never change `generate_cloud_init_script()` to use the official image!**

See `hetzner_manager.py:200` for detailed documentation on why.

#!/bin/bash
# CloudBot EC2 Instance Bootstrap Script
# Full desktop environment with Chrome, VS Code, LibreOffice

# Log all output
exec > >(tee /var/log/user-data.log) 2>&1

echo "=== CloudBot Instance Setup Starting ==="
echo "Date: $(date)"

# Create swap file
echo "Creating swap file..."
fallocate -l 4G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab

# Update package list
echo "Updating packages..."
apt-get update -y

# Install XFCE desktop environment (full)
echo "Installing XFCE desktop..."
DEBIAN_FRONTEND=noninteractive apt-get install -y \
    xfce4 \
    xfce4-terminal \
    xfce4-taskmanager \
    xfce4-whiskermenu-plugin \
    xfce4-panel-profiles \
    xfce4-screenshooter \
    thunar \
    mousepad \
    dbus-x11 \
    at-spi2-core \
    libglib2.0-bin \
    xdg-utils \
    adwaita-icon-theme-full \
    papirus-icon-theme \
    fonts-noto \
    fonts-noto-color-emoji
apt-get clean

# Install VNC server + virtual framebuffer
echo "Installing VNC..."
DEBIAN_FRONTEND=noninteractive apt-get install -y x11vnc xvfb

# Install screenshot and input tools for computer use
echo "Installing computer use tools (scrot, xdotool, imagemagick)..."
DEBIAN_FRONTEND=noninteractive apt-get install -y scrot xdotool imagemagick

# Install basic tools
echo "Installing basic tools..."
DEBIAN_FRONTEND=noninteractive apt-get install -y \
    git curl wget python3-pip unzip software-properties-common \
    ca-certificates gnupg lsb-release

# Install Google Chrome
echo "Installing Google Chrome..."
wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
DEBIAN_FRONTEND=noninteractive apt-get install -y /tmp/chrome.deb || true
rm -f /tmp/chrome.deb
apt-get clean

# Install VS Code
echo "Installing VS Code..."
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /usr/share/keyrings/packages.microsoft.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list
apt-get update -y
DEBIAN_FRONTEND=noninteractive apt-get install -y code
apt-get clean

# Install LibreOffice
echo "Installing LibreOffice..."
DEBIAN_FRONTEND=noninteractive apt-get install -y libreoffice-calc libreoffice-writer libreoffice-impress
apt-get clean

# Install Firefox as backup browser
DEBIAN_FRONTEND=noninteractive apt-get install -y firefox

# Install Node.js 22 (required for moltbot)
echo "Installing Node.js 22..."
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
apt-get install -y nodejs
node --version
npm --version

# Enable corepack for pnpm
corepack enable

# Install OpenClaw AI Gateway
echo "Setting up OpenClaw gateway..."

OPENCLAW_INSTALLED=false

# Download CloudBot tarball from S3
CLOUDBOT_TARBALL_URL="https://cloudbot-moltbot-assets.s3.amazonaws.com/openclaw.tgz"

if [ -n "$CLOUDBOT_TARBALL_URL" ]; then
  echo "Installing CloudBot from $CLOUDBOT_TARBALL_URL..."

  # Download tarball
  curl -fsSL "$CLOUDBOT_TARBALL_URL" -o /tmp/openclaw.tgz

  if [ -f /tmp/openclaw.tgz ]; then
    # Install globally
    echo "=== STARTING NPM GLOBAL INSTALL ==="
    echo "Tarball size: $(ls -la /tmp/openclaw.tgz)"
    echo "NPM version: $(npm --version)"
    echo "Node version: $(node --version)"

    echo "Running: npm install -g /tmp/openclaw.tgz"

    # Capture full output
    NPM_OUTPUT=$(npm install -g /tmp/openclaw.tgz 2>&1)
    NPM_EXIT_CODE=$?
    echo "=== NPM OUTPUT START ==="
    echo "$NPM_OUTPUT"
    echo "=== NPM OUTPUT END ==="
    echo "NPM exit code: $NPM_EXIT_CODE"

    if [ $NPM_EXIT_CODE -eq 0 ]; then
      echo "npm install succeeded"
    else
      echo "npm install FAILED with exit code $NPM_EXIT_CODE"
    fi
    rm -f /tmp/openclaw.tgz

    # Find where npm installed the binaries
    NPM_PREFIX=$(npm config get prefix)
    NPM_GLOBAL_ROOT=$(npm root -g)
    echo "=== BINARY SEARCH ==="
    echo "NPM prefix: $NPM_PREFIX"
    echo "NPM global root: $NPM_GLOBAL_ROOT"

    echo "=== NPM BIN DIRECTORY ==="
    echo "All files in $NPM_PREFIX/bin:"
    ls -la "$NPM_PREFIX/bin/" 2>/dev/null || echo "Cannot list $NPM_PREFIX/bin"

    echo "=== CHECK OPENCLAW PACKAGE DIRECTORY ==="
    if [ -d "$NPM_GLOBAL_ROOT/openclaw" ]; then
      echo "openclaw package exists at $NPM_GLOBAL_ROOT/openclaw"
      echo "Contents:"
      ls -la "$NPM_GLOBAL_ROOT/openclaw/" 2>/dev/null | head -20
      echo "Package.json bin field:"
      cat "$NPM_GLOBAL_ROOT/openclaw/package.json" 2>/dev/null | grep -A5 '"bin"' || echo "No bin field found"
      echo "openclaw.mjs exists:"
      ls -la "$NPM_GLOBAL_ROOT/openclaw/openclaw.mjs" 2>/dev/null || echo "openclaw.mjs NOT FOUND"
    else
      echo "openclaw package NOT found in $NPM_GLOBAL_ROOT"
      echo "Available packages in global node_modules:"
      ls -la "$NPM_GLOBAL_ROOT/" 2>/dev/null | head -20
    fi

    echo "=== WHICH COMMANDS ==="
    which openclaw 2>/dev/null && echo "which openclaw: found" || echo "which openclaw: not found"
    which node 2>/dev/null && echo "which node: $(which node)"
    which npm 2>/dev/null && echo "which npm: $(which npm)"

    # Check multiple locations
    echo "=== CHECKING STANDARD BIN LOCATIONS ==="
    for loc in "$NPM_PREFIX/bin/openclaw" /usr/local/bin/openclaw /usr/bin/openclaw; do
      if [ -e "$loc" ]; then
        echo "  EXISTS: $loc"
        ls -la "$loc" 2>/dev/null
      else
        echo "  NOT FOUND: $loc"
      fi
    done

    # Also check for npm global packages
    echo "=== NPM GLOBAL PACKAGES ==="
    npm list -g --depth=0 2>/dev/null || echo "Cannot list global packages"

    # Try to find and use the binary
    if [ -x "$NPM_PREFIX/bin/openclaw" ]; then
      echo "OpenClaw found at $NPM_PREFIX/bin/openclaw"
      ln -sf "$NPM_PREFIX/bin/openclaw" /usr/local/bin/openclaw
      OPENCLAW_INSTALLED=true
    elif [ -x /usr/local/bin/openclaw ]; then
      echo "OpenClaw found at /usr/local/bin/openclaw"
      OPENCLAW_INSTALLED=true
    elif [ -x /usr/bin/openclaw ]; then
      echo "OpenClaw found at /usr/bin/openclaw"
      ln -sf /usr/bin/openclaw /usr/local/bin/openclaw
      OPENCLAW_INSTALLED=true
    else
      echo "=== OPENCLAW NOT FOUND - WILL USE FALLBACK ==="
    fi
  else
    echo "FATAL: Failed to download OpenClaw tarball"
  fi
else
  echo "FATAL: No CONTROL_PLANE_URL or MOLTBOT_TARBALL_URL provided - cannot install OpenClaw"
fi

# OpenClaw MUST be installed - no fallback
if [ "$OPENCLAW_INSTALLED" = false ]; then
  echo "=== FATAL ERROR: OpenClaw failed to install ==="
  echo "OpenClaw is required. Check the logs above for installation errors."
  echo "Common issues:"
  echo "  - Tarball URL not set (CONTROL_PLANE_URL or MOLTBOT_TARBALL_URL)"
  echo "  - Tarball download failed"
  echo "  - npm install -g failed"
  echo "  - Binary not created in expected location"
  # Don't exit - continue to see what else fails
fi

echo "OpenClaw/Gateway setup complete (openclaw installed: $OPENCLAW_INSTALLED)"

# Set up desktop wallpaper and theme
echo "Configuring desktop appearance..."
mkdir -p /root/.config/xfce4/xfconf/xfce-perchannel-xml
mkdir -p /usr/share/backgrounds/cloudbot

# Download CloudBot wallpaper from control-plane
WALLPAPER_PATH="/usr/share/backgrounds/cloudbot/wallpaper.jpg"
if [ -n "$CONTROL_PLANE_URL" ]; then
  WALLPAPER_URL="${CONTROL_PLANE_URL}/assets/wallpaper.jpg"
  echo "Downloading wallpaper from $WALLPAPER_URL..."
  curl -fsSL "$WALLPAPER_URL" -o "$WALLPAPER_PATH" 2>/dev/null || {
    echo "Wallpaper download failed, using dark background"
    WALLPAPER_PATH=""
  }
else
  echo "No CONTROL_PLANE_URL set, using dark background"
  WALLPAPER_PATH=""
fi

# XFCE desktop settings - use wallpaper if available, otherwise black background
if [ -n "$WALLPAPER_PATH" ] && [ -f "$WALLPAPER_PATH" ]; then
  cat > /root/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml <<DESKEOF
<?xml version="1.0" encoding="UTF-8"?>
<channel name="xfce4-desktop" version="1.0">
  <property name="backdrop" type="empty">
    <property name="screen0" type="empty">
      <property name="monitorscreen" type="empty">
        <property name="workspace0" type="empty">
          <property name="color-style" type="int" value="0"/>
          <property name="rgba1" type="array">
            <value type="double" value="0.0"/>
            <value type="double" value="0.0"/>
            <value type="double" value="0.0"/>
            <value type="double" value="1.0"/>
          </property>
          <property name="image-style" type="int" value="5"/>
          <property name="last-image" type="string" value="$WALLPAPER_PATH"/>
        </property>
      </property>
    </property>
  </property>
</channel>
DESKEOF
  echo "Wallpaper configured: $WALLPAPER_PATH"
else
  cat > /root/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml <<'DESKEOF'
<?xml version="1.0" encoding="UTF-8"?>
<channel name="xfce4-desktop" version="1.0">
  <property name="backdrop" type="empty">
    <property name="screen0" type="empty">
      <property name="monitorscreen" type="empty">
        <property name="workspace0" type="empty">
          <property name="color-style" type="int" value="0"/>
          <property name="rgba1" type="array">
            <value type="double" value="0.0"/>
            <value type="double" value="0.0"/>
            <value type="double" value="0.0"/>
            <value type="double" value="1.0"/>
          </property>
          <property name="image-style" type="int" value="0"/>
        </property>
      </property>
    </property>
  </property>
</channel>
DESKEOF
fi

# XFCE window manager - Greybird theme + single workspace
cat > /root/.config/xfce4/xfconf/xfce-perchannel-xml/xfwm4.xml <<'WMEOF'
<?xml version="1.0" encoding="UTF-8"?>
<channel name="xfwm4" version="1.0">
  <property name="general" type="empty">
    <property name="theme" type="string" value="Greybird-dark"/>
    <property name="title_font" type="string" value="Noto Sans Bold 10"/>
    <property name="workspace_count" type="int" value="1"/>
  </property>
</channel>
WMEOF

# GTK theme - dark
mkdir -p /root/.config/gtk-3.0
cat > /root/.config/gtk-3.0/settings.ini <<'GTKEOF'
[Settings]
gtk-theme-name=Adwaita-dark
gtk-icon-theme-name=Papirus-Dark
gtk-font-name=Noto Sans 10
gtk-cursor-theme-name=Adwaita
GTKEOF

# XFCE panel (bottom taskbar with dock-like launchers) - dark black background
cat > /root/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml <<'PANELEOF'
<?xml version="1.0" encoding="UTF-8"?>
<channel name="xfce4-panel" version="1.0">
  <property name="configver" type="int" value="2"/>
  <property name="panels" type="array">
    <value type="int" value="1"/>
    <property name="dark-mode" type="bool" value="true"/>
    <property name="panel-1" type="empty">
      <property name="position" type="string" value="p=8;x=640;y=698"/>
      <property name="length" type="uint" value="100"/>
      <property name="position-locked" type="bool" value="true"/>
      <property name="icon-size" type="uint" value="32"/>
      <property name="size" type="uint" value="40"/>
      <property name="background-style" type="uint" value="1"/>
      <property name="background-rgba" type="array">
        <value type="double" value="0.05"/>
        <value type="double" value="0.05"/>
        <value type="double" value="0.05"/>
        <value type="double" value="0.95"/>
      </property>
      <property name="plugin-ids" type="array">
        <value type="int" value="1"/>
        <value type="int" value="2"/>
        <value type="int" value="3"/>
        <value type="int" value="4"/>
        <value type="int" value="5"/>
        <value type="int" value="6"/>
        <value type="int" value="10"/>
        <value type="int" value="11"/>
        <value type="int" value="12"/>
        <value type="int" value="13"/>
      </property>
    </property>
  </property>
  <property name="plugins" type="empty">
    <property name="plugin-1" type="string" value="whiskermenu"/>
    <property name="plugin-2" type="string" value="separator">
      <property name="style" type="uint" value="0"/>
    </property>
    <property name="plugin-3" type="string" value="launcher">
      <property name="items" type="array">
        <value type="string" value="thunar.desktop"/>
      </property>
    </property>
    <property name="plugin-4" type="string" value="launcher">
      <property name="items" type="array">
        <value type="string" value="xfce4-terminal.desktop"/>
      </property>
    </property>
    <property name="plugin-5" type="string" value="launcher">
      <property name="items" type="array">
        <value type="string" value="google-chrome.desktop"/>
      </property>
    </property>
    <property name="plugin-6" type="string" value="launcher">
      <property name="items" type="array">
        <value type="string" value="code.desktop"/>
      </property>
    </property>
    <property name="plugin-10" type="string" value="separator">
      <property name="expand" type="bool" value="true"/>
      <property name="style" type="uint" value="0"/>
    </property>
    <property name="plugin-11" type="string" value="tasklist">
      <property name="flat-buttons" type="bool" value="true"/>
      <property name="show-labels" type="bool" value="true"/>
    </property>
    <property name="plugin-12" type="string" value="systray"/>
    <property name="plugin-13" type="string" value="clock">
      <property name="digital-format" type="string" value="%H:%M"/>
    </property>
  </property>
</channel>
PANELEOF

# Create .desktop files for Chrome (run without sandbox for root)
mkdir -p /usr/share/applications
cat > /usr/share/applications/google-chrome.desktop <<'CHREOF'
[Desktop Entry]
Version=1.0
Name=Google Chrome
Comment=Access the Internet
Exec=/usr/bin/google-chrome-stable --no-sandbox --disable-gpu --disable-software-rasterizer --disable-dev-shm-usage --disable-extensions --disable-background-networking --disable-sync --no-first-run --disable-translate %U
StartupNotify=true
Terminal=false
Icon=google-chrome
Type=Application
Categories=Network;WebBrowser;
MimeType=text/html;text/xml;application/xhtml+xml;
CHREOF

# VS Code desktop file (run without sandbox for root)
cat > /usr/share/applications/code.desktop <<'CODEEOF'
[Desktop Entry]
Version=1.0
Name=VS Code
Comment=Code Editor
Exec=/usr/bin/code --no-sandbox --unity-launch %F
StartupNotify=true
Terminal=false
Icon=vscode
Type=Application
Categories=Development;IDE;
MimeType=text/plain;
CODEEOF

# Configure Xvfb service (1920x1080 virtual display)
cat > /etc/systemd/system/xvfb.service <<'EOF'
[Unit]
Description=X Virtual Frame Buffer
After=network.target

[Service]
ExecStart=/usr/bin/Xvfb :99 -screen 0 1920x1080x24 -ac +render -noreset
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Configure x11vnc service
cat > /etc/systemd/system/x11vnc.service <<'EOF'
[Unit]
Description=x11vnc VNC Server
After=xvfb.service
Requires=xvfb.service

[Service]
Environment=DISPLAY=:99
ExecStartPre=/bin/sleep 2
ExecStart=/usr/bin/x11vnc -display :99 -forever -shared -rfbport 5900 -nopw -threads -clip 1920x1080+0+0
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Configure XFCE session service with proper D-Bus session
cat > /etc/systemd/system/xfce-session.service <<'EOF'
[Unit]
Description=XFCE Desktop Session
After=xvfb.service dbus.service
Requires=xvfb.service
Wants=dbus.service

[Service]
Type=simple
Environment=DISPLAY=:99
Environment=HOME=/root
Environment=USER=root
Environment=XDG_CONFIG_DIRS=/etc/xdg
Environment=XDG_DATA_DIRS=/usr/local/share:/usr/share
Environment=XDG_RUNTIME_DIR=/run/user/0
ExecStartPre=/bin/mkdir -p /run/user/0
ExecStartPre=/bin/chmod 700 /run/user/0
ExecStartPre=/bin/sleep 3
ExecStart=/usr/bin/dbus-launch --exit-with-session /usr/bin/startxfce4
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Create OpenClaw config directory and workspace
mkdir -p /root/.openclaw
mkdir -p /root/cloudbot-workspace
mkdir -p /root/cloudbot-workspace/projects

# ============================================
# MEMORY SYSTEM - Task/Project Management
# ============================================

# Create MEMORIES.md - Cross-session memory for learnings and preferences
cat > /root/cloudbot-workspace/MEMORIES.md <<'MEMORIESMD'
# CloudBot Memories

This file stores persistent memories across all sessions. CloudBot reads this at session start and updates it when learning new things.

## User Preferences
<!-- Agent learns and records user preferences here -->
<!-- Example: "User prefers dark themes", "User likes concise responses" -->

## Important Context
<!-- Key facts about user, their work, environment -->
<!-- Example: "User works on web development projects", "User's timezone is PST" -->

## Past Learnings
<!-- Lessons learned from completed tasks -->
<!-- Example: "The deploy script requires sudo", "User's repo uses pnpm not npm" -->

## Frequently Used
<!-- Common commands, paths, tools the user prefers -->
<!-- Example: "User often opens Chrome first", "User's projects are in ~/dev" -->
MEMORIESMD

# Create TASKS.md - Master task index
cat > /root/cloudbot-workspace/TASKS.md <<'TASKSMD'
# Task Index

This is the master list of all tasks. Check this at session start to see pending work.

## Active Tasks
| ID | Name | Project | Status | Priority | Last Updated |
|----|------|---------|--------|----------|--------------|
<!-- Active tasks go here -->

## Quick Tasks
<!-- Simple one-off tasks without a project -->
<!-- Example: - [ ] Download file from URL -->

## Completed Tasks
<!-- Move tasks here when done, with completion date -->
<!-- Example: - [x] Set up Chrome (2024-01-15) -->
TASKSMD

# Create AGENTS.md - Main agent instructions with memory system
cat > /root/cloudbot-workspace/AGENTS.md <<'AGENTSMD'
# CloudBot Agent

You are CloudBot, a personal AI assistant with **persistent memory** running on a cloud desktop.

## On Session Start - ALWAYS DO THIS

1. **Read MEMORIES.md** - Recall user preferences and context
2. **Check TASKS.md** - See if there's pending work
3. **List projects/** - Check for ongoing projects (ls projects/)
4. **Greet appropriately**:
   - If pending work: "I see we were working on [X]. Want to continue?"
   - If no pending work: Normal greeting

## Task Management

### Assessing Work Complexity
When user asks for something, decide:

- **Quick task** (< 5 min, single action): Do immediately, optionally log
- **Standard task** (multi-step): Log in TASKS.md, then execute
- **Project** (complex, multi-session): Create project folder with full structure

### Creating a Project
For complex work that may span multiple sessions:

```bash
PROJECT="project-name"
mkdir -p projects/$PROJECT/artifacts
```

Then create these files in projects/$PROJECT/:
- **README.md** - Overview, goals, requirements
- **PLAN.md** - Implementation approach and phases
- **STATUS.md** - CRITICAL: Current state for resuming work
- **TASKS.md** - Project-specific task breakdown
- **NOTES.md** - Research notes and learnings

### Updating Progress - CRITICAL
- **ALWAYS update STATUS.md** before ending work on a project
- Mark completed items in TASKS.md
- Add learnings to NOTES.md or workspace MEMORIES.md

### Resuming Work
1. Read project STATUS.md for where you left off
2. Check project TASKS.md for next steps
3. Continue from last checkpoint

## Memory Protocol

### What to Remember (in MEMORIES.md)
- User's name, role, preferences
- Coding style preferences
- Frequently used tools/paths
- Important decisions made
- Lessons from past mistakes

### What NOT to Remember
- Sensitive credentials (use env vars)
- Temporary/one-off information
- Duplicates of project-specific info

## Available Tools
- Full Ubuntu desktop with XFCE
- Google Chrome browser (--no-sandbox for root)
- VS Code editor (--no-sandbox for root)
- LibreOffice suite (Calc, Writer, Impress)
- Terminal/bash with full system access
- Computer-use tools for desktop control
- File system read/write access

## Project Template

When creating a new project, use this structure:

**projects/{slug}/README.md:**
```markdown
# Project Name
## Goal
What we're trying to achieve
## Requirements
- Requirement 1
## Status: 🟡 In Progress
```

**projects/{slug}/STATUS.md:**
```markdown
# Status - Last Updated: [timestamp]
## Current Phase: [phase]
## What's Done: [list]
## What's Next: [next step]
## Blockers: [any blockers]
```
AGENTSMD

# Create IDENTITY.md
cat > /root/cloudbot-workspace/IDENTITY.md <<'IDENTITYMD'
# CloudBot Identity

- Name: CloudBot
- Type: AI assistant with persistent memory
- Vibe: Helpful, organized, remembers everything
- Emoji: 🤖
- Special: Maintains continuity across sessions
IDENTITYMD

# Create SOUL.md - Memory-aware personality
cat > /root/cloudbot-workspace/SOUL.md <<'SOULMD'
# CloudBot Soul

CloudBot is a **persistent AI assistant** that maintains continuity across sessions through its memory system.

## Core Behaviors

### Memory-First Approach
- ALWAYS check MEMORIES.md and TASKS.md at session start
- Proactively mention pending work to user
- Remember and apply user preferences
- Learn from past interactions

### Project-Oriented Mindset
- Organize complex work into projects with clear structure
- Maintain STATUS.md so work can resume anytime
- Break large tasks into trackable sub-tasks
- Keep artifacts organized in project folders

### Proactive Communication
- "I see we were working on X. Want to continue?"
- "I remember you prefer Y. Should I use that?"
- "Based on our last session, I think we should..."
- "I've updated the project status for next time."

### Progress Tracking
- Keep STATUS.md current (most important!)
- Update TASKS.md as work progresses
- Never lose track of where we are
- Document blockers and next steps

## Personality
- Helpful and efficient
- Organized and methodical
- Has a good memory, learns from experience
- Asks before assuming on important decisions
- Professional but friendly

## Key Principles
1. **Continuity**: Sessions should flow seamlessly
2. **Organization**: Complex work gets proper structure
3. **Transparency**: Always clear about current state
4. **Learning**: Improve from past interactions
SOULMD

# Create USER.md - Agent can update this with learned info
cat > /root/cloudbot-workspace/USER.md <<'USERMD'
# User Profile

CloudBot updates this file as it learns about the user.

## Basic Info
- Name: (to be learned)
- Preferred address: (to be learned)

## Preferences
- (Agent adds learned preferences)

## Working Style
- (Agent observes and records)

## Notes
- New user, preferences not yet known
USERMD

# Create TOOLS.md
cat > /root/cloudbot-workspace/TOOLS.md <<'TOOLSMD'
# Tool Notes

## Browser - Google Chrome
- Launch: `google-chrome-stable --no-sandbox`
- Use for web browsing and research
- Can automate with computer-use tools

## Editor - VS Code
- Launch: `code --no-sandbox`
- Use for coding tasks
- Supports most languages

## Office - LibreOffice
- Writer: `libreoffice --writer` (documents)
- Calc: `libreoffice --calc` (spreadsheets)
- Impress: `libreoffice --impress` (presentations)

## Terminal
- Full bash access
- Can install packages with apt
- Run any command

## File System
- Workspace: /root/cloudbot-workspace
- Projects: /root/cloudbot-workspace/projects/
- Full read/write access to system
TOOLSMD

echo "CloudBot workspace with memory system created"
ls -la /root/cloudbot-workspace/

# Build openclaw.json with full agent configuration
# dangerouslyDisableDeviceAuth: true bypasses device pairing for web clients
cat > /root/.openclaw/openclaw.json <<'OPENCLAWCFG'
{
  "gateway": {
    "mode": "local",
    "bind": "lan",
    "port": 18789,
    "auth": {
      "mode": "password",
      "password": "cloudbot-gateway-secret"
    },
    "controlUi": {
      "dangerouslyDisableDeviceAuth": true,
      "allowedOrigins": ["https://cloudbot-ai.com", "http://localhost:5173", "http://localhost:3000"]
    }
  },
  "agents": {
    "defaults": {
      "workspace": "/root/cloudbot-workspace",
      "thinkingDefault": "off",
      "model": {
        "primary": "anthropic/claude-sonnet-4-5-20250929"
      }
    },
    "list": [
      {
        "id": "cloudbot",
        "default": true,
        "workspace": "/root/cloudbot-workspace",
        "model": {
          "primary": "anthropic/claude-sonnet-4-5-20250929"
        },
        "identity": {
          "name": "CloudBot",
          "theme": "cloud desktop assistant",
          "emoji": "🤖"
        }
      }
    ]
  },
  "browser": {
    "enabled": true,
    "headless": true,
    "noSandbox": true
  },
  "computerUse": {
    "enabled": true,
    "displayWidth": 1280,
    "displayHeight": 800,
    "screenWidth": 1920,
    "screenHeight": 1080,
    "displayNum": 99
  }
}
OPENCLAWCFG

echo "OpenClaw workspace created at /root/cloudbot-workspace"
ls -la /root/cloudbot-workspace/

# Log which API keys are configured (without showing values)
echo "=== API Keys Available ==="
[ -n "$ANTHROPIC_API_KEY" ] && echo "  - ANTHROPIC_API_KEY: set"
[ -n "$OPENAI_API_KEY" ] && echo "  - OPENAI_API_KEY: set"
[ -n "$GOOGLE_API_KEY" ] && echo "  - GOOGLE_API_KEY: set"
[ -n "$GROQ_API_KEY" ] && echo "  - GROQ_API_KEY: set"
[ -n "$TOGETHER_API_KEY" ] && echo "  - TOGETHER_API_KEY: set"
[ -n "$OPENROUTER_API_KEY" ] && echo "  - OPENROUTER_API_KEY: set"
[ -n "$MISTRAL_API_KEY" ] && echo "  - MISTRAL_API_KEY: set"
[ -n "$DEEPSEEK_API_KEY" ] && echo "  - DEEPSEEK_API_KEY: set"
[ -n "$XAI_API_KEY" ] && echo "  - XAI_API_KEY: set"

echo "OpenClaw config contents:"
cat /root/.openclaw/openclaw.json

# Create environment file for openclaw service with API keys
echo "=== Creating /etc/openclaw.env ==="
cat > /etc/openclaw.env <<ENVFILE
DISPLAY=:99
HOME=/root
OPENCLAW_GATEWAY_PASSWORD=cloudbot-gateway-secret
ENVFILE

# Append API keys to environment file (no quotes - systemd EnvironmentFile format)
# IMPORTANT: Use printf to avoid $ expansion in API keys
if [ -n "$ANTHROPIC_API_KEY" ]; then
  printf 'ANTHROPIC_API_KEY=%s\n' "$ANTHROPIC_API_KEY" >> /etc/openclaw.env
  echo "Added ANTHROPIC_API_KEY to /etc/openclaw.env (length: ${#ANTHROPIC_API_KEY})"
fi
[ -n "$OPENAI_API_KEY" ] && printf 'OPENAI_API_KEY=%s\n' "$OPENAI_API_KEY" >> /etc/openclaw.env && echo "Added OPENAI_API_KEY"
[ -n "$GOOGLE_API_KEY" ] && printf 'GOOGLE_API_KEY=%s\n' "$GOOGLE_API_KEY" >> /etc/openclaw.env && echo "Added GOOGLE_API_KEY"
[ -n "$GROQ_API_KEY" ] && printf 'GROQ_API_KEY=%s\n' "$GROQ_API_KEY" >> /etc/openclaw.env && echo "Added GROQ_API_KEY"
[ -n "$TOGETHER_API_KEY" ] && printf 'TOGETHER_API_KEY=%s\n' "$TOGETHER_API_KEY" >> /etc/openclaw.env && echo "Added TOGETHER_API_KEY"
[ -n "$OPENROUTER_API_KEY" ] && printf 'OPENROUTER_API_KEY=%s\n' "$OPENROUTER_API_KEY" >> /etc/openclaw.env && echo "Added OPENROUTER_API_KEY"
[ -n "$MISTRAL_API_KEY" ] && printf 'MISTRAL_API_KEY=%s\n' "$MISTRAL_API_KEY" >> /etc/openclaw.env && echo "Added MISTRAL_API_KEY"
[ -n "$DEEPSEEK_API_KEY" ] && printf 'DEEPSEEK_API_KEY=%s\n' "$DEEPSEEK_API_KEY" >> /etc/openclaw.env && echo "Added DEEPSEEK_API_KEY"
[ -n "$XAI_API_KEY" ] && printf 'XAI_API_KEY=%s\n' "$XAI_API_KEY" >> /etc/openclaw.env && echo "Added XAI_API_KEY"

echo "=== Contents of /etc/openclaw.env (redacted) ==="
cat /etc/openclaw.env | sed 's/=.*/=***REDACTED***/'

chmod 600 /etc/openclaw.env

# Configure systemd service - ONLY use real OpenClaw (no fallback)
if [ "$OPENCLAW_INSTALLED" = true ]; then
  echo "Configuring openclaw service for REAL openclaw..."
  cat > /etc/systemd/system/openclaw.service <<'EOF'
[Unit]
Description=OpenClaw Gateway
After=network.target xvfb.service
Requires=xvfb.service

[Service]
Type=simple
EnvironmentFile=/etc/openclaw.env
WorkingDirectory=/root/cloudbot-workspace
Environment=DISPLAY=:99
Environment=HOME=/root
Environment=OPENCLAW_GATEWAY_PASSWORD=cloudbot-gateway-secret
Environment=NODE_OPTIONS=--max-old-space-size=1024
ExecStart=/usr/local/bin/openclaw gateway --verbose --bind lan --port 18789 --auth password
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
  echo "OpenClaw gateway service configured (real openclaw)"
fi

# Enable and start services
echo "Starting services..."
systemctl daemon-reload
systemctl enable xvfb x11vnc xfce-session openclaw
systemctl start xvfb
sleep 3
systemctl start x11vnc
sleep 2
systemctl start xfce-session
sleep 5
echo "Starting OpenClaw gateway..."
systemctl start openclaw

# Verify services
echo "=== Service Status ==="
systemctl is-active xvfb && echo "Xvfb: OK" || echo "Xvfb: FAILED"
systemctl is-active x11vnc && echo "x11vnc: OK" || echo "x11vnc: FAILED"
systemctl is-active xfce-session && echo "XFCE: OK" || echo "XFCE: FAILED"
systemctl is-active openclaw && echo "OpenClaw: OK" || echo "OpenClaw: FAILED"

# Wait a moment and verify OpenClaw is actually listening
sleep 10
echo "=== Port Check ==="
ss -tlnp | grep 18789 && echo "OpenClaw listening on 18789: OK" || {
  echo "OpenClaw not listening on 18789, checking logs..."
  journalctl -u openclaw --no-pager -n 50

  echo "Attempting manual restart..."
  systemctl restart openclaw
  sleep 10

  ss -tlnp | grep 18789 && echo "OpenClaw gateway now listening: OK" || {
    echo "Systemd restart failed, trying to run gateway directly..."

    # Source the environment file and run directly
    set -a
    source /etc/openclaw.env
    set +a

    # Only try real OpenClaw - no fallback
    echo "Testing openclaw binary..."
    openclaw --version > /var/log/openclaw-version.log 2>&1 || echo "openclaw --version failed"
    cat /var/log/openclaw-version.log

    echo "Starting OpenClaw gateway directly..."
    cd /root/cloudbot-workspace
    DISPLAY=:99 HOME=/root NODE_OPTIONS="--max-old-space-size=1024" nohup /usr/local/bin/openclaw gateway --verbose --bind lan --port 18789 --auth password > /var/log/openclaw-direct.log 2>&1 &
    OPENCLAW_PID=$!
    echo "Started OpenClaw gateway directly with PID: $OPENCLAW_PID"

    # Wait longer for OpenClaw to fully initialize (it starts browser/chrome)
    echo "Waiting 60 seconds for OpenClaw to fully start..."
    for i in 1 2 3 4 5 6; do
      sleep 10
      if ss -tlnp | grep -q 18789; then
        echo "Openclaw listening on 18789 after $((i*10)) seconds"
        break
      fi
      echo "Check $i: not listening yet..."
    done

    ss -tlnp | grep 18789 && echo "Gateway running directly: OK" || {
      echo "=== OpenClaw failed to start. Checking logs... ==="
      cat /var/log/openclaw-direct.log 2>/dev/null || echo "(no logs)"
      ps aux | grep -i openclaw || true
      echo "=== OpenClaw FAILED - No fallback available ==="
    }
  }
}

# Create watchdog script to restart OpenClaw gateway if not listening
cat > /etc/cron.d/openclaw-watchdog <<'CRON'
* * * * * root ss -tlnp | grep -q 18789 || systemctl restart openclaw
CRON
chmod 644 /etc/cron.d/openclaw-watchdog

# Create a simple debug HTTP server to serve logs
cat > /opt/debug-server.py <<'DEBUGPY'
#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess

class LogHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/log' or self.path == '/':
            try:
                with open('/var/log/user-data.log', 'r') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(content.encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(str(e).encode())
        elif self.path == '/check':
            checks = []
            checks.append(f"which openclaw: {subprocess.getoutput('which openclaw 2>/dev/null || echo NOT_FOUND')}")
            checks.append(f"npm prefix: {subprocess.getoutput('npm config get prefix')}")
            checks.append(f"npm root -g: {subprocess.getoutput('npm root -g')}")
            checks.append(f"ls npm bin: {subprocess.getoutput('ls -la $(npm config get prefix)/bin/ 2>/dev/null | head -20')}")
            checks.append(f"npm list -g: {subprocess.getoutput('npm list -g --depth=0 2>/dev/null')}")
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write('\n\n'.join(checks).encode())
        elif self.path == '/debug':
            logs = []
            logs.append("=== openclaw version ===")
            logs.append(subprocess.getoutput('cat /var/log/openclaw-version.log 2>/dev/null || echo "(not found)"'))
            logs.append("\n=== openclaw-direct.log ===")
            logs.append(subprocess.getoutput('cat /var/log/openclaw-direct.log 2>/dev/null || echo "(not found)"'))
            logs.append("\n=== openclaw service status ===")
            logs.append(subprocess.getoutput('systemctl status openclaw 2>/dev/null || echo "(not available)"'))
            logs.append("\n=== openclaw journal ===")
            logs.append(subprocess.getoutput('journalctl -u openclaw --no-pager -n 100 2>/dev/null || echo "(not available)"'))
            logs.append("\n=== processes on 18789 ===")
            logs.append(subprocess.getoutput('ss -tlnp | grep 18789 || echo "(nothing listening)"'))
            logs.append("\n=== ps aux openclaw ===")
            logs.append(subprocess.getoutput('ps aux | grep -i openclaw | grep -v grep || echo "(not running)"'))
            logs.append("\n=== openclaw detailed log ===")
            logs.append(subprocess.getoutput('tail -100 /tmp/openclaw/openclaw-*.log 2>/dev/null || echo "(no log file)"'))
            # Check openclaw process environment for ANTHROPIC_API_KEY
            logs.append("\n=== openclaw process env (ANTHROPIC_API_KEY) ===")
            logs.append(subprocess.getoutput('pid=$(pgrep -f "openclaw-gateway" | head -1); if [ -n "$pid" ]; then cat /proc/$pid/environ 2>/dev/null | tr "\\0" "\\n" | grep ANTHROPIC_API_KEY | sed "s/=.*/=***REDACTED***/"; else echo "(openclaw not running)"; fi'))
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write('\n'.join(logs).encode())
            return
        elif self.path == '/testapi':
            import os
            key = os.environ.get('ANTHROPIC_API_KEY', '')
            key_info = f"len={len(key)}, start={key[:15]}..., end=...{key[-4:]}" if key else "NOT SET"
            # Read from env file
            file_key = ""
            try:
                with open('/etc/openclaw.env', 'r') as f:
                    for line in f:
                        if line.startswith('ANTHROPIC_API_KEY='):
                            file_key = line.split('=', 1)[1].strip()
            except Exception as e:
                file_key = f"ERR:{e}"
            file_info = f"len={len(file_key)}, start={file_key[:15]}..., end=...{file_key[-4:]}" if file_key and len(file_key) > 20 else file_key or "NOT IN FILE"
            match = "MATCH" if key == file_key else "MISMATCH"
            # Test API with env key
            import urllib.request
            import json as jsonlib
            test1 = "?"
            try:
                req = urllib.request.Request('https://api.anthropic.com/v1/messages',
                    data=jsonlib.dumps({"model": "claude-3-haiku-20240307", "max_tokens": 10, "messages": [{"role": "user", "content": "hi"}]}).encode(),
                    headers={'Content-Type': 'application/json', 'x-api-key': key, 'anthropic-version': '2023-06-01'})
                with urllib.request.urlopen(req, timeout=10) as r: test1 = f"OK:{r.status}"
            except urllib.error.HTTPError as e: test1 = f"HTTP:{e.code}"
            except Exception as e: test1 = f"ERR:{e}"
            # Test API with file key
            test2 = "?"
            try:
                req = urllib.request.Request('https://api.anthropic.com/v1/messages',
                    data=jsonlib.dumps({"model": "claude-3-haiku-20240307", "max_tokens": 10, "messages": [{"role": "user", "content": "hi"}]}).encode(),
                    headers={'Content-Type': 'application/json', 'x-api-key': file_key, 'anthropic-version': '2023-06-01'})
                with urllib.request.urlopen(req, timeout=10) as r: test2 = f"OK:{r.status}"
            except urllib.error.HTTPError as e: test2 = f"HTTP:{e.code}"
            except Exception as e: test2 = f"ERR:{e}"
            # Test with sonnet model (same as OpenClaw uses)
            test3 = "?"
            try:
                req = urllib.request.Request('https://api.anthropic.com/v1/messages',
                    data=jsonlib.dumps({"model": "claude-sonnet-4-20250514", "max_tokens": 50, "messages": [{"role": "user", "content": "say hello"}]}).encode(),
                    headers={'Content-Type': 'application/json', 'x-api-key': file_key, 'anthropic-version': '2023-06-01'})
                with urllib.request.urlopen(req, timeout=30) as r:
                    resp = jsonlib.loads(r.read().decode())
                    text = resp.get('content', [{}])[0].get('text', '')[:50]
                    test3 = f"OK:{r.status} '{text}'"
            except urllib.error.HTTPError as e: test3 = f"HTTP:{e.code}-{e.read().decode()[:100]}"
            except Exception as e: test3 = f"ERR:{e}"
            result = f"Bash env: {key_info}\nEnv file: {file_info}\nKeys: {match}\nTest haiku: {test1}\nTest file key: {test2}\nTest sonnet-4: {test3}"
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(result.encode())
            return
        else:
            self.send_response(404)
            self.end_headers()

HTTPServer(('0.0.0.0', 8080), LogHandler).serve_forever()
DEBUGPY

chmod +x /opt/debug-server.py
nohup python3 /opt/debug-server.py > /var/log/debug-server.log 2>&1 &
echo "Debug server started on port 8080"

echo "=== CloudBot Instance Setup Complete ==="
echo "VNC running on port 5900"
echo "OpenClaw gateway running on port 18789"
echo "Debug server running on port 8080"
echo "Resolution: 1920x1080"
echo "Date: $(date)"

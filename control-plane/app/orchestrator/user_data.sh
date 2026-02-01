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

# Download OpenClaw tarball - try control-plane first, then fallback to MOLTBOT_TARBALL_URL
OPENCLAW_TARBALL_URL=""
if [ -n "$CONTROL_PLANE_URL" ]; then
  OPENCLAW_TARBALL_URL="${CONTROL_PLANE_URL}/assets/openclaw.tgz"
elif [ -n "$MOLTBOT_TARBALL_URL" ]; then
  OPENCLAW_TARBALL_URL="$MOLTBOT_TARBALL_URL"
fi

if [ -n "$OPENCLAW_TARBALL_URL" ]; then
  echo "Installing OpenClaw from $OPENCLAW_TARBALL_URL..."

  # Download tarball
  curl -fsSL "$OPENCLAW_TARBALL_URL" -o /tmp/openclaw.tgz

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
    echo "Failed to download OpenClaw tarball, falling back to simple gateway"
  fi
else
  echo "No CONTROL_PLANE_URL or MOLTBOT_TARBALL_URL provided, using simple gateway"
fi

# If real moltbot not installed, create fallback simple gateway
if [ "$OPENCLAW_INSTALLED" = false ]; then
  echo "Setting up fallback simple gateway..."
  mkdir -p /opt/cloudbot-gateway
  cd /opt/cloudbot-gateway

  # Install ws package for WebSocket server
  npm init -y
  npm install ws

  # Create the simple gateway server (follows moltbot/clawdbot protocol)
  cat > /opt/cloudbot-gateway/server.js << 'GATEWAYSERVER'
const WebSocket = require('ws');
const https = require('https');

const PORT = 18789;
const PASSWORD = 'cloudbot-gateway-secret';
const PING_INTERVAL = 30000;

const wss = new WebSocket.Server({ port: PORT, host: '0.0.0.0' });
console.log(`Simple CloudBot gateway started on port ${PORT}`);

function heartbeat() { this.isAlive = true; }

const pingInterval = setInterval(() => {
  wss.clients.forEach((ws) => {
    if (ws.isAlive === false) return ws.terminate();
    ws.isAlive = false;
    ws.ping();
  });
}, PING_INTERVAL);

wss.on('close', () => clearInterval(pingInterval));

async function callAnthropic(apiKey, messages) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({ model: 'claude-sonnet-4-20250514', max_tokens: 4096, messages });
    const req = https.request({
      hostname: 'api.anthropic.com', port: 443, path: '/v1/messages', method: 'POST',
      headers: { 'Content-Type': 'application/json', 'x-api-key': apiKey, 'anthropic-version': '2023-06-01' }
    }, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(body);
          if (json.content && json.content[0]) resolve(json.content[0].text);
          else if (json.error) reject(new Error(json.error.message));
          else reject(new Error('Unexpected response format'));
        } catch (e) { reject(e); }
      });
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

const sessions = new Map();

wss.on('connection', function connection(ws, req) {
  console.log('Client connected from', req.socket.remoteAddress);
  let authenticated = false;
  const apiKey = process.env.ANTHROPIC_API_KEY;
  ws.isAlive = true;
  ws.on('pong', heartbeat);

  ws.send(JSON.stringify({ type: 'event', event: 'connect.challenge', payload: { methods: ['password'] } }));

  ws.on('message', async function message(data) {
    try {
      const msg = JSON.parse(data.toString());
      if (msg.type === 'req') {
        const { id, method, params } = msg;
        if (method === 'connect') {
          if (params?.auth?.password === PASSWORD) {
            authenticated = true;
            ws.send(JSON.stringify({ type: 'res', id, ok: true, payload: { type: 'hello-ok', protocol: 1, server: { id: 'cloudbot-simple', displayName: 'CloudBot Simple Gateway', version: '1.0.0' } } }));
          } else {
            ws.send(JSON.stringify({ type: 'res', id, ok: false, error: { code: 'auth_failed', message: 'Authentication failed' } }));
          }
          return;
        }
        if (!authenticated) { ws.send(JSON.stringify({ type: 'res', id, ok: false, error: { code: 'not_authenticated', message: 'Not authenticated' } })); return; }
        if (method === 'chat.send') {
          const { sessionKey, message: userMessage } = params;
          const runId = `run-${Date.now()}`;
          if (!sessions.has(sessionKey)) sessions.set(sessionKey, []);
          const history = sessions.get(sessionKey);
          ws.send(JSON.stringify({ type: 'res', id, ok: true, payload: { status: 'started', runId } }));
          history.push({ role: 'user', content: userMessage });
          if (!apiKey) { ws.send(JSON.stringify({ type: 'event', event: 'chat', payload: { runId, state: 'final', message: { role: 'assistant', content: [{ type: 'text', text: 'No API key configured.' }] } } })); return; }
          try {
            const response = await callAnthropic(apiKey, history);
            history.push({ role: 'assistant', content: response });
            ws.send(JSON.stringify({ type: 'event', event: 'chat', payload: { runId, state: 'final', message: { role: 'assistant', content: [{ type: 'text', text: response }] } } }));
          } catch (error) { ws.send(JSON.stringify({ type: 'event', event: 'chat', payload: { runId, state: 'error', errorMessage: `API error: ${error.message}` } })); }
          return;
        }
        ws.send(JSON.stringify({ type: 'res', id, ok: false, error: { code: 'unknown_method', message: `Unknown method: ${method}` } }));
      }
    } catch (e) { console.error('Parse error:', e); }
  });
  ws.on('close', () => console.log('Client disconnected'));
  ws.on('error', (err) => console.error('WebSocket error:', err));
});
GATEWAYSERVER
fi

echo "OpenClaw/Gateway setup complete (real openclaw: $OPENCLAW_INSTALLED)"

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

# Create workspace files for the agent
cat > /root/cloudbot-workspace/AGENTS.md <<'AGENTSMD'
# CloudBot Agent

You are CloudBot, a personal AI assistant running on a cloud desktop. You have access to:

- A full Ubuntu desktop with XFCE
- Google Chrome browser
- VS Code editor
- LibreOffice suite

## Capabilities

You can help users with:
- Research and web browsing
- Document creation and editing
- Code writing and development
- File management
- General computer tasks

## Tools

You have access to the computer-use tools to control the desktop.
AGENTSMD

cat > /root/cloudbot-workspace/IDENTITY.md <<'IDENTITYMD'
# CloudBot Identity

- Name: CloudBot
- Creature: AI assistant
- Vibe: Helpful, efficient, knowledgeable
- Emoji: 🤖
IDENTITYMD

cat > /root/cloudbot-workspace/SOUL.md <<'SOULMD'
# CloudBot Soul

CloudBot is a helpful AI assistant that runs on a cloud desktop. It provides direct, practical assistance to users through conversation and computer control.

## Personality
- Friendly but professional
- Direct and efficient
- Focused on solving problems
- Patient with explanations

## Approach
- Listen carefully to user requests
- Execute tasks efficiently
- Explain what you're doing when helpful
- Ask clarifying questions when needed
SOULMD

cat > /root/cloudbot-workspace/USER.md <<'USERMD'
# User Profile

- Name: CloudBot User
- Preferred address: User
- Notes: General cloud desktop user
USERMD

cat > /root/cloudbot-workspace/TOOLS.md <<'TOOLSMD'
# Tool Notes

## Browser
- Use Chrome for web browsing
- Headless mode for automation

## Editor
- VS Code for coding tasks
- Open files with code command

## Office
- LibreOffice for documents, spreadsheets, presentations
TOOLSMD

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
      "dangerouslyDisableDeviceAuth": true
    }
  },
  "agents": {
    "defaults": {
      "workspace": "/root/cloudbot-workspace",
      "skipBootstrap": true
    },
    "list": [
      {
        "id": "cloudbot",
        "default": true,
        "workspace": "/root/cloudbot-workspace",
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

# Append API keys to environment file (with proper quoting for special chars)
if [ -n "$ANTHROPIC_API_KEY" ]; then
  echo "ANTHROPIC_API_KEY='$ANTHROPIC_API_KEY'" >> /etc/openclaw.env
  echo "Added ANTHROPIC_API_KEY to /etc/openclaw.env (length: ${#ANTHROPIC_API_KEY})"
fi
[ -n "$OPENAI_API_KEY" ] && echo "OPENAI_API_KEY='$OPENAI_API_KEY'" >> /etc/openclaw.env && echo "Added OPENAI_API_KEY"
[ -n "$GOOGLE_API_KEY" ] && echo "GOOGLE_API_KEY='$GOOGLE_API_KEY'" >> /etc/openclaw.env && echo "Added GOOGLE_API_KEY"
[ -n "$GROQ_API_KEY" ] && echo "GROQ_API_KEY='$GROQ_API_KEY'" >> /etc/openclaw.env && echo "Added GROQ_API_KEY"
[ -n "$TOGETHER_API_KEY" ] && echo "TOGETHER_API_KEY='$TOGETHER_API_KEY'" >> /etc/openclaw.env && echo "Added TOGETHER_API_KEY"
[ -n "$OPENROUTER_API_KEY" ] && echo "OPENROUTER_API_KEY='$OPENROUTER_API_KEY'" >> /etc/openclaw.env && echo "Added OPENROUTER_API_KEY"
[ -n "$MISTRAL_API_KEY" ] && echo "MISTRAL_API_KEY='$MISTRAL_API_KEY'" >> /etc/openclaw.env && echo "Added MISTRAL_API_KEY"
[ -n "$DEEPSEEK_API_KEY" ] && echo "DEEPSEEK_API_KEY='$DEEPSEEK_API_KEY'" >> /etc/openclaw.env && echo "Added DEEPSEEK_API_KEY"
[ -n "$XAI_API_KEY" ] && echo "XAI_API_KEY='$XAI_API_KEY'" >> /etc/openclaw.env && echo "Added XAI_API_KEY"

echo "=== Contents of /etc/openclaw.env (redacted) ==="
cat /etc/openclaw.env | sed 's/=.*/=***REDACTED***/'

chmod 600 /etc/openclaw.env

# Configure CloudBot gateway service - use web-compatible gateway
# Note: Real openclaw requires device pairing which web clients can't provide
# The CloudBot gateway provides equivalent chat functionality for web users
mkdir -p /opt/cloudbot-gateway
cd /opt/cloudbot-gateway

# Install ws if needed
if [ ! -f /opt/cloudbot-gateway/node_modules/ws/package.json ]; then
  npm init -y
  npm install ws
fi

# Create the CloudBot gateway server
cat > /opt/cloudbot-gateway/server.js << 'GATEWAYSERVER'
const WebSocket = require('ws');
const https = require('https');

const PORT = 18789;
const PASSWORD = 'cloudbot-gateway-secret';
const PING_INTERVAL = 30000;

const wss = new WebSocket.Server({ port: PORT, host: '0.0.0.0' });
console.log(`CloudBot Gateway started on port ${PORT}`);

function heartbeat() { this.isAlive = true; }

const pingInterval = setInterval(() => {
  wss.clients.forEach((ws) => {
    if (ws.isAlive === false) return ws.terminate();
    ws.isAlive = false;
    ws.ping();
  });
}, PING_INTERVAL);

wss.on('close', () => clearInterval(pingInterval));

async function callAnthropic(apiKey, messages) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({ model: 'claude-sonnet-4-20250514', max_tokens: 4096, messages });
    const req = https.request({
      hostname: 'api.anthropic.com', port: 443, path: '/v1/messages', method: 'POST',
      headers: { 'Content-Type': 'application/json', 'x-api-key': apiKey, 'anthropic-version': '2023-06-01' }
    }, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(body);
          if (json.content && json.content[0]) resolve(json.content[0].text);
          else if (json.error) reject(new Error(json.error.message));
          else reject(new Error('Unexpected response format'));
        } catch (e) { reject(e); }
      });
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

const sessions = new Map();

wss.on('connection', function connection(ws, req) {
  console.log('Client connected from', req.socket.remoteAddress);
  let authenticated = false;
  const apiKey = process.env.ANTHROPIC_API_KEY;
  ws.isAlive = true;
  ws.on('pong', heartbeat);

  ws.send(JSON.stringify({ type: 'event', event: 'connect.challenge', payload: { methods: ['password'] } }));

  ws.on('message', async function message(data) {
    try {
      const msg = JSON.parse(data.toString());
      if (msg.type === 'req') {
        const { id, method, params } = msg;
        if (method === 'connect') {
          if (params?.auth?.password === PASSWORD) {
            authenticated = true;
            ws.send(JSON.stringify({ type: 'res', id, ok: true, payload: { type: 'hello-ok', protocol: 1, server: { id: 'cloudbot', displayName: 'CloudBot Gateway', version: '1.0.0' } } }));
          } else {
            ws.send(JSON.stringify({ type: 'res', id, ok: false, error: { code: 'auth_failed', message: 'Authentication failed' } }));
          }
          return;
        }
        if (!authenticated) { ws.send(JSON.stringify({ type: 'res', id, ok: false, error: { code: 'not_authenticated', message: 'Not authenticated' } })); return; }
        if (method === 'chat.send') {
          const { sessionKey, message: userMessage } = params;
          const runId = `run-${Date.now()}`;
          if (!sessions.has(sessionKey)) sessions.set(sessionKey, []);
          const history = sessions.get(sessionKey);
          ws.send(JSON.stringify({ type: 'res', id, ok: true, payload: { status: 'started', runId } }));
          history.push({ role: 'user', content: userMessage });
          if (!apiKey) { ws.send(JSON.stringify({ type: 'event', event: 'chat', payload: { runId, state: 'final', message: { role: 'assistant', content: [{ type: 'text', text: 'No API key configured. Please add your Anthropic API key when creating the instance.' }] } } })); return; }
          try {
            const response = await callAnthropic(apiKey, history);
            history.push({ role: 'assistant', content: response });
            ws.send(JSON.stringify({ type: 'event', event: 'chat', payload: { runId, state: 'final', message: { role: 'assistant', content: [{ type: 'text', text: response }] } } }));
          } catch (error) { ws.send(JSON.stringify({ type: 'event', event: 'chat', payload: { runId, state: 'error', errorMessage: `API error: ${error.message}` } })); }
          return;
        }
        ws.send(JSON.stringify({ type: 'res', id, ok: false, error: { code: 'unknown_method', message: `Unknown method: ${method}` } }));
      }
    } catch (e) { console.error('Parse error:', e); }
  });
  ws.on('close', () => console.log('Client disconnected'));
  ws.on('error', (err) => console.error('WebSocket error:', err));
});
GATEWAYSERVER

# Configure systemd service based on whether real openclaw is installed
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
ExecStart=/usr/local/bin/openclaw gateway --verbose --bind lan --port 18789 --auth password --password cloudbot-gateway-secret
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
  echo "OpenClaw gateway service configured (real openclaw)"
else
  echo "Configuring openclaw service for fallback gateway..."
  cat > /etc/systemd/system/openclaw.service <<'EOF'
[Unit]
Description=OpenClaw Gateway (Fallback)
After=network.target

[Service]
Type=simple
EnvironmentFile=/etc/openclaw.env
WorkingDirectory=/opt/cloudbot-gateway
ExecStart=/usr/bin/node /opt/cloudbot-gateway/server.js
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
  echo "OpenClaw fallback gateway service configured"
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

    # Check if real openclaw or simple gateway
    if [ "$OPENCLAW_INSTALLED" = true ]; then
      # Try running real openclaw gateway directly
      cd /root

      # First test if openclaw can run at all
      echo "Testing openclaw binary..."
      openclaw --version > /var/log/openclaw-version.log 2>&1 || echo "openclaw --version failed"
      cat /var/log/openclaw-version.log

      echo "Starting OpenClaw gateway..."
      # Use full path and ensure environment is passed
      cd /root/cloudbot-workspace
      DISPLAY=:99 HOME=/root nohup /usr/local/bin/openclaw gateway --verbose --bind lan --port 18789 --auth password --password cloudbot-gateway-secret > /var/log/openclaw-direct.log 2>&1 &
      OPENCLAW_PID=$!
      echo "Started real OpenClaw gateway directly with PID: $OPENCLAW_PID"
    else
      # Try running simple gateway directly
      cd /opt/cloudbot-gateway
      nohup node server.js > /var/log/cloudbot-direct.log 2>&1 &
      GATEWAY_PID=$!
      echo "Started simple gateway directly with PID: $GATEWAY_PID"
    fi

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
      echo "Direct run failed after 60s, checking logs..."
      if [ "$OPENCLAW_INSTALLED" = true ]; then
        echo "=== openclaw-direct.log ==="
        cat /var/log/openclaw-direct.log 2>/dev/null || echo "(empty or not found)"
        echo "=== checking process ==="
        ps aux | grep -i openclaw || true
        echo "=== checking if process crashed ==="
        dmesg | tail -20 || true

        # Real OpenClaw failed completely, fall back to simple gateway
        echo "Real OpenClaw failed, setting up simple gateway as fallback..."
        mkdir -p /opt/cloudbot-gateway
        cd /opt/cloudbot-gateway

        # Install ws if needed
        if [ ! -f /opt/cloudbot-gateway/node_modules/ws/package.json ]; then
          npm init -y
          npm install ws
        fi

        # Create the simple gateway server
        cat > /opt/cloudbot-gateway/server.js << 'FALLBACKSERVER'
const WebSocket = require('ws');
const https = require('https');

const PORT = 18789;
const PASSWORD = 'cloudbot-gateway-secret';
const PING_INTERVAL = 30000;

const wss = new WebSocket.Server({ port: PORT, host: '0.0.0.0' });
console.log(`Simple CloudBot gateway (fallback) started on port ${PORT}`);

function heartbeat() { this.isAlive = true; }

const pingInterval = setInterval(() => {
  wss.clients.forEach((ws) => {
    if (ws.isAlive === false) return ws.terminate();
    ws.isAlive = false;
    ws.ping();
  });
}, PING_INTERVAL);

wss.on('close', () => clearInterval(pingInterval));

async function callAnthropic(apiKey, messages) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({ model: 'claude-sonnet-4-20250514', max_tokens: 4096, messages });
    const req = https.request({
      hostname: 'api.anthropic.com', port: 443, path: '/v1/messages', method: 'POST',
      headers: { 'Content-Type': 'application/json', 'x-api-key': apiKey, 'anthropic-version': '2023-06-01' }
    }, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(body);
          if (json.content && json.content[0]) resolve(json.content[0].text);
          else if (json.error) reject(new Error(json.error.message));
          else reject(new Error('Unexpected response format'));
        } catch (e) { reject(e); }
      });
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

const sessions = new Map();

wss.on('connection', function connection(ws, req) {
  console.log('Client connected from', req.socket.remoteAddress);
  let authenticated = false;
  const apiKey = process.env.ANTHROPIC_API_KEY;
  ws.isAlive = true;
  ws.on('pong', heartbeat);

  ws.send(JSON.stringify({ type: 'event', event: 'connect.challenge', payload: { methods: ['password'] } }));

  ws.on('message', async function message(data) {
    try {
      const msg = JSON.parse(data.toString());
      if (msg.type === 'req') {
        const { id, method, params } = msg;
        if (method === 'connect') {
          if (params?.auth?.password === PASSWORD) {
            authenticated = true;
            ws.send(JSON.stringify({ type: 'res', id, ok: true, payload: { type: 'hello-ok', protocol: 1, server: { id: 'cloudbot-fallback', displayName: 'CloudBot Fallback Gateway', version: '1.0.0' } } }));
          } else {
            ws.send(JSON.stringify({ type: 'res', id, ok: false, error: { code: 'auth_failed', message: 'Authentication failed' } }));
          }
          return;
        }
        if (!authenticated) { ws.send(JSON.stringify({ type: 'res', id, ok: false, error: { code: 'not_authenticated', message: 'Not authenticated' } })); return; }
        if (method === 'chat.send') {
          const { sessionKey, message: userMessage } = params;
          const runId = `run-${Date.now()}`;
          if (!sessions.has(sessionKey)) sessions.set(sessionKey, []);
          const history = sessions.get(sessionKey);
          ws.send(JSON.stringify({ type: 'res', id, ok: true, payload: { status: 'started', runId } }));
          history.push({ role: 'user', content: userMessage });
          if (!apiKey) { ws.send(JSON.stringify({ type: 'event', event: 'chat', payload: { runId, state: 'final', message: { role: 'assistant', content: [{ type: 'text', text: 'No API key configured. Please add your Anthropic API key in settings.' }] } } })); return; }
          try {
            const response = await callAnthropic(apiKey, history);
            history.push({ role: 'assistant', content: response });
            ws.send(JSON.stringify({ type: 'event', event: 'chat', payload: { runId, state: 'final', message: { role: 'assistant', content: [{ type: 'text', text: response }] } } }));
          } catch (error) { ws.send(JSON.stringify({ type: 'event', event: 'chat', payload: { runId, state: 'error', errorMessage: `API error: ${error.message}` } })); }
          return;
        }
        ws.send(JSON.stringify({ type: 'res', id, ok: false, error: { code: 'unknown_method', message: `Unknown method: ${method}` } }));
      }
    } catch (e) { console.error('Parse error:', e); }
  });
  ws.on('close', () => console.log('Client disconnected'));
  ws.on('error', (err) => console.error('WebSocket error:', err));
});
FALLBACKSERVER

        # Run the fallback simple gateway
        nohup node /opt/cloudbot-gateway/server.js > /var/log/cloudbot-fallback.log 2>&1 &
        FALLBACK_PID=$!
        echo "Started fallback simple gateway with PID: $FALLBACK_PID"

        sleep 5
        ss -tlnp | grep 18789 && echo "Fallback gateway running: OK" || {
          echo "Fallback gateway also failed"
          cat /var/log/cloudbot-fallback.log 2>/dev/null | tail -20 || true
        }
      else
        cat /var/log/cloudbot-direct.log 2>/dev/null | tail -50 || true
        echo "All gateway start methods failed"
      fi
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
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write('\n'.join(logs).encode())
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

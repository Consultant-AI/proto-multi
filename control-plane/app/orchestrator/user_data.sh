#!/bin/bash
# CloudBot EC2 Instance Bootstrap Script
# Full desktop environment with Chrome, VS Code, LibreOffice

# Log all output
exec > >(tee /var/log/user-data.log) 2>&1

echo "=== CloudBot Instance Setup Starting ==="
echo "Date: $(date)"

# Create swap file
echo "Creating swap file..."
fallocate -l 2G /swapfile
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

# Install Moltbot/CloudBot AI Gateway
echo "Setting up Moltbot gateway..."

MOLTBOT_INSTALLED=false

# Check if we have a tarball URL for real moltbot
if [ -n "$MOLTBOT_TARBALL_URL" ]; then
  echo "Installing real Moltbot from $MOLTBOT_TARBALL_URL..."

  # Download tarball
  curl -fsSL "$MOLTBOT_TARBALL_URL" -o /tmp/moltbot.tgz

  if [ -f /tmp/moltbot.tgz ]; then
    # Install globally
    npm install -g /tmp/moltbot.tgz
    rm -f /tmp/moltbot.tgz

    # Verify installation
    if command -v moltbot &> /dev/null; then
      echo "Moltbot installed successfully: $(moltbot --version 2>/dev/null || echo 'version unknown')"
      MOLTBOT_INSTALLED=true
    else
      echo "Moltbot command not found after install, falling back to simple gateway"
    fi
  else
    echo "Failed to download moltbot tarball, falling back to simple gateway"
  fi
else
  echo "No MOLTBOT_TARBALL_URL provided, using simple gateway"
fi

# If real moltbot not installed, create fallback simple gateway
if [ "$MOLTBOT_INSTALLED" = false ]; then
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

echo "Moltbot/Gateway setup complete (real moltbot: $MOLTBOT_INSTALLED)"

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

# Create moltbot config directory (correct path is ~/.clawdbot/)
mkdir -p /root/.clawdbot

# Build moltbot.json with password auth and browser settings
# The password must match what ChatInterface.tsx sends in the connect request
cat > /root/.clawdbot/moltbot.json <<'MOLTCFG'
{
  "gateway": {
    "mode": "local",
    "bind": "lan",
    "port": 18789,
    "auth": {
      "mode": "password",
      "password": "cloudbot-gateway-secret"
    }
  },
  "browser": {
    "enabled": true,
    "headless": false,
    "noSandbox": true
  }
}
MOLTCFG

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

echo "Moltbot config contents:"
cat /root/.clawdbot/moltbot.json

# Create environment file for moltbot service with API keys
cat > /etc/moltbot.env <<ENVFILE
DISPLAY=:99
HOME=/root
ENVFILE

# Append API keys to environment file
[ -n "$ANTHROPIC_API_KEY" ] && echo "ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY" >> /etc/moltbot.env
[ -n "$OPENAI_API_KEY" ] && echo "OPENAI_API_KEY=$OPENAI_API_KEY" >> /etc/moltbot.env
[ -n "$GOOGLE_API_KEY" ] && echo "GOOGLE_API_KEY=$GOOGLE_API_KEY" >> /etc/moltbot.env
[ -n "$GROQ_API_KEY" ] && echo "GROQ_API_KEY=$GROQ_API_KEY" >> /etc/moltbot.env
[ -n "$TOGETHER_API_KEY" ] && echo "TOGETHER_API_KEY=$TOGETHER_API_KEY" >> /etc/moltbot.env
[ -n "$OPENROUTER_API_KEY" ] && echo "OPENROUTER_API_KEY=$OPENROUTER_API_KEY" >> /etc/moltbot.env
[ -n "$MISTRAL_API_KEY" ] && echo "MISTRAL_API_KEY=$MISTRAL_API_KEY" >> /etc/moltbot.env
[ -n "$DEEPSEEK_API_KEY" ] && echo "DEEPSEEK_API_KEY=$DEEPSEEK_API_KEY" >> /etc/moltbot.env
[ -n "$XAI_API_KEY" ] && echo "XAI_API_KEY=$XAI_API_KEY" >> /etc/moltbot.env

chmod 600 /etc/moltbot.env

# Configure Moltbot gateway service - use real moltbot if installed, else simple gateway
if [ "$MOLTBOT_INSTALLED" = true ]; then
  # Real moltbot service
  cat > /etc/systemd/system/moltbot.service <<'EOF'
[Unit]
Description=Moltbot AI Gateway (Real)
After=xfce-session.service network.target
Requires=xvfb.service
Wants=xfce-session.service

[Service]
Type=simple
EnvironmentFile=/etc/moltbot.env
Environment=CLAWDBOT_SKIP_CHANNELS=1
WorkingDirectory=/root
ExecStartPre=/bin/sleep 5
ExecStart=/usr/bin/moltbot gateway --verbose
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
  echo "Real moltbot service configured"
else
  # Simple fallback gateway service
  cat > /etc/systemd/system/moltbot.service <<'EOF'
[Unit]
Description=CloudBot Simple Gateway
After=xfce-session.service network.target
Requires=xvfb.service
Wants=xfce-session.service

[Service]
Type=simple
EnvironmentFile=/etc/moltbot.env
WorkingDirectory=/opt/cloudbot-gateway
ExecStartPre=/bin/sleep 2
ExecStart=/usr/bin/node /opt/cloudbot-gateway/server.js
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
  echo "Simple gateway service configured"
fi

# Enable and start services
echo "Starting services..."
systemctl daemon-reload
systemctl enable xvfb x11vnc xfce-session moltbot
systemctl start xvfb
sleep 3
systemctl start x11vnc
sleep 2
systemctl start xfce-session
sleep 5
echo "Starting moltbot gateway..."
systemctl start moltbot

# Verify services
echo "=== Service Status ==="
systemctl is-active xvfb && echo "Xvfb: OK" || echo "Xvfb: FAILED"
systemctl is-active x11vnc && echo "x11vnc: OK" || echo "x11vnc: FAILED"
systemctl is-active xfce-session && echo "XFCE: OK" || echo "XFCE: FAILED"
systemctl is-active moltbot && echo "Moltbot: OK" || echo "Moltbot: FAILED"

# Wait a moment and verify moltbot is actually listening
sleep 10
echo "=== Port Check ==="
ss -tlnp | grep 18789 && echo "Moltbot listening on 18789: OK" || {
  echo "Moltbot not listening on 18789, checking logs..."
  journalctl -u moltbot --no-pager -n 50

  echo "Attempting manual restart..."
  systemctl restart moltbot
  sleep 10

  ss -tlnp | grep 18789 && echo "CloudBot gateway now listening: OK" || {
    echo "Systemd restart failed, trying to run gateway directly..."

    # Source the environment file and run directly
    set -a
    source /etc/moltbot.env
    set +a

    # Try running gateway directly in background
    cd /opt/cloudbot-gateway
    nohup node server.js > /var/log/cloudbot-direct.log 2>&1 &
    CLOUDBOT_PID=$!
    echo "Started CloudBot gateway directly with PID: $CLOUDBOT_PID"

    sleep 5
    ss -tlnp | grep 18789 && echo "CloudBot gateway running directly: OK" || {
      echo "Direct run failed, checking logs..."
      cat /var/log/cloudbot-direct.log 2>/dev/null | tail -50 || true
      echo "All CloudBot gateway start methods failed"
    }
  }
}

# Create watchdog script to restart CloudBot gateway if not listening
cat > /etc/cron.d/cloudbot-watchdog <<'CRON'
* * * * * root ss -tlnp | grep -q 18789 || systemctl restart moltbot
CRON
chmod 644 /etc/cron.d/cloudbot-watchdog

echo "=== CloudBot Instance Setup Complete ==="
echo "VNC running on port 5900"
echo "Moltbot gateway running on port 18789"
echo "Resolution: 1920x1080"
echo "Date: $(date)"

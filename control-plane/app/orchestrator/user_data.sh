#!/bin/bash
# CloudBot EC2 Instance Bootstrap Script

set -e

# Log all output
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

echo "=== CloudBot Instance Setup Starting ==="

# Update system
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get upgrade -y

# Install desktop environment (GNOME)
echo "Installing GNOME desktop..."
DEBIAN_FRONTEND=noninteractive apt-get install -y ubuntu-desktop-minimal gnome-session gdm3

# Install applications
echo "Installing applications..."
apt-get install -y firefox chromium-browser git curl wget
snap install code --classic
apt-get install -y libreoffice python3-pip

# Install VNC server
echo "Installing VNC server..."
apt-get install -y x11vnc xvfb

# Install Node.js 22
echo "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
apt-get install -y nodejs

# Install CloudBot (moltbot)
echo "Installing CloudBot..."
npm install -g moltbot@latest

# Configure VNC - Xvfb service
cat > /etc/systemd/system/xvfb.service <<'EOF'
[Unit]
Description=X Virtual Frame Buffer Service
After=network.target

[Service]
ExecStart=/usr/bin/Xvfb :99 -screen 0 1920x1080x24
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF

# Configure VNC - x11vnc service
cat > /etc/systemd/system/x11vnc.service <<'EOF'
[Unit]
Description=x11vnc VNC Server
After=xvfb.service
Requires=xvfb.service

[Service]
Environment=DISPLAY=:99
ExecStart=/usr/bin/x11vnc -display :99 -forever -shared -rfbport 5900 -nopw
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF

# Configure GNOME session service
cat > /etc/systemd/system/gnome-session.service <<'EOF'
[Unit]
Description=GNOME Session
After=xvfb.service
Requires=xvfb.service

[Service]
Environment=DISPLAY=:99
Environment=XDG_SESSION_TYPE=x11
ExecStart=/usr/bin/gnome-session
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF

# CloudBot configuration directory
mkdir -p /root/.clawdbot

# CloudBot config (will be updated via API with user's API keys)
cat > /root/.clawdbot/config.yaml <<'EOF'
gateway:
  bind: 0.0.0.0
  port: 18789

agents:
  list:
    - id: default
      name: CloudBot Agent
      model:
        provider: anthropic
        model: claude-sonnet-4-5-20250929

# Disable messaging channels (not needed for cloud platform)
channels: {}

# Enable local tools only
tools:
  browser:
    enabled: true
  exec:
    enabled: true
    ask: false  # Auto-approve for now (can be made more restrictive)
EOF

# CloudBot systemd service
cat > /etc/systemd/system/cloudbot.service <<'EOF'
[Unit]
Description=CloudBot Gateway
After=network.target

[Service]
Environment=CLAWDBOT_STATE_DIR=/root/.clawdbot
Environment=DISPLAY=:99
ExecStart=/usr/local/bin/moltbot gateway --bind 0.0.0.0 --port 18789
Restart=always
WorkingDirectory=/root
User=root

[Install]
WantedBy=multi-user.target
EOF

# Enable and start services
systemctl daemon-reload
systemctl enable xvfb x11vnc gnome-session cloudbot
systemctl start xvfb
sleep 2
systemctl start x11vnc
systemctl start gnome-session
sleep 5
systemctl start cloudbot

# Check service status
echo "=== Service Status ==="
systemctl status xvfb --no-pager || true
systemctl status x11vnc --no-pager || true
systemctl status gnome-session --no-pager || true
systemctl status cloudbot --no-pager || true

echo "=== CloudBot Instance Setup Complete ==="
echo "VNC running on port 5900"
echo "CloudBot running on port 18789"

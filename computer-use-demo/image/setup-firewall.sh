#!/bin/bash
# Firewall rules to prevent unauthorized network scanning

echo "Setting up firewall rules..."

# Install iptables-persistent to save rules
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y iptables-persistent

# Flush existing rules
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X

# Default policies
iptables -P INPUT ACCEPT
iptables -P FORWARD DROP
iptables -P OUTPUT DROP

# Allow loopback
iptables -A OUTPUT -o lo -j ACCEPT
iptables -A INPUT -i lo -j ACCEPT

# Allow established connections
iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow incoming SSH (port 22)
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Allow incoming HTTP services (8080, 8501, 6080)
iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
iptables -A INPUT -p tcp --dport 8501 -j ACCEPT
iptables -A INPUT -p tcp --dport 6080 -j ACCEPT

# Allow DNS queries (both TCP and UDP)
iptables -A OUTPUT -p udp --dport 53 -j ACCEPT
iptables -A OUTPUT -p tcp --dport 53 -j ACCEPT

# Allow HTTP/HTTPS for package downloads and web browsing
iptables -A OUTPUT -p tcp --dport 80 -j ACCEPT
iptables -A OUTPUT -p tcp --dport 443 -j ACCEPT

# Allow NTP (time sync)
iptables -A OUTPUT -p udp --dport 123 -j ACCEPT

# Block all VNC ports (5900-5909) to prevent scanning
iptables -A OUTPUT -p tcp --dport 5900:5909 -j REJECT
iptables -A OUTPUT -p udp --dport 5900:5909 -j REJECT

# Block common scanning ports
iptables -A OUTPUT -p tcp --dport 23 -j REJECT    # Telnet
iptables -A OUTPUT -p tcp --dport 3389 -j REJECT  # RDP
iptables -A OUTPUT -p tcp --dport 445 -j REJECT   # SMB
iptables -A OUTPUT -p tcp --dport 139 -j REJECT   # NetBIOS

# Log dropped packets (for debugging)
iptables -A OUTPUT -m limit --limit 5/min -j LOG --log-prefix "iptables-dropped: " --log-level 4

# Save rules
netfilter-persistent save

echo "✅ Firewall rules configured"
echo "   - Blocked VNC scanning ports (5900-5909)"
echo "   - Blocked common attack ports"
echo "   - Allowed only necessary outbound traffic"


#!/usr/bin/env bash
set -euo pipefail

echo "=================================="
echo " LINKTICKET WEB - Nginx Install"
echo "=================================="

# Check operating system
if ! grep -q 'Amazon Linux' /etc/os-release; then
    echo "ERROR: Amazon Linux is required."
    exit 1
fi

# Check root privileges
if [[ "$(id -u)" -ne 0 ]]; then
    echo "ERROR: Run this script as root."
    exit 1
fi

echo "[1/4] Installing Nginx"
dnf install -y nginx

echo "[2/4] Enabling Nginx"
systemctl enable nginx

echo "[3/4] Checking Nginx version"
nginx -v

echo "[4/4] Installation complete"
echo "Nginx installed successfully."
echo "Configuration and deployment will be performed separately."

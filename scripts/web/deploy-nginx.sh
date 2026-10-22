
#!/usr/bin/env bash
set -euo pipefail

# LINKTICKET Nginx deployment
# Usage: sudo bash deploy-nginx.sh <WAS_PRIVATE_IP>

if [[ "$(id -u)" -ne 0 ]]; then
    echo "ERROR: Run as root."
    exit 1
fi

if [[ $# -ne 1 ]]; then
    echo "Usage: sudo bash $0 <WAS_PRIVATE_IP>"
    exit 1
fi

WAS_HOST="$1"

if [[ ! "$WAS_HOST" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "ERROR: A WAS IPv4 address is required."
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_CONF="${SCRIPT_DIR}/linkticket-nginx.conf"
TARGET_CONF="/etc/nginx/conf.d/linkticket.conf"

if [[ ! -f "$SOURCE_CONF" ]]; then
    echo "ERROR: Nginx configuration template not found."
    exit 1
fi

echo "[1/4] Rendering Nginx configuration"
sed "s/\${WAS_HOST}/${WAS_HOST}/g" "$SOURCE_CONF" > "$TARGET_CONF"

echo "[2/4] Validating Nginx configuration"
nginx -t

echo "[3/4] Enabling Nginx"
systemctl enable nginx

echo "[4/4] Starting or reloading Nginx"
if systemctl is-active --quiet nginx; then
    systemctl reload nginx
else
    systemctl start nginx
fi

echo "Nginx deployment completed."

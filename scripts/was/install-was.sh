
#!/usr/bin/env bash
set -euo pipefail

# LINKTICKET AWS WAS base installation
# Target OS: Amazon Linux 2023

if [[ "$(id -u)" -ne 0 ]]; then
    echo "ERROR: Run as root."
    exit 1
fi

if ! grep -q "Amazon Linux" /etc/os-release; then
    echo "ERROR: Amazon Linux is required."
    exit 1
fi

echo "[1/5] Updating package metadata"
dnf makecache

echo "[2/5] Installing Python and tools"
dnf install -y python3 python3-pip git

echo "[3/5] Creating application account"
if ! id linkticket &>/dev/null; then
    useradd --system --create-home --shell /sbin/nologin linkticket
fi

echo "[4/5] Creating directories"
install -d -o linkticket -g linkticket -m 0750 /var/www/ticket_app
install -d -o root -g linkticket -m 0750 /etc/linkticket

echo "[5/5] Checking Python"
python3 --version
python3 -m pip --version

echo "WAS base installation completed."

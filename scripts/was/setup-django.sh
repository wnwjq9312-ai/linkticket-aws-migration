
#!/usr/bin/env bash
set -euo pipefail

# LINKTICKET AWS Django environment setup
# Run after the application source has been deployed.

APP_DIR="/var/www/ticket_app"
VENV_DIR="${APP_DIR}/.venv"
REQ_FILE="${APP_DIR}/deploy/requirements-py39.txt"

if [[ "$(id -u)" -ne 0 ]]; then
    echo "ERROR: Run as root."
    exit 1
fi

if [[ ! -f "$REQ_FILE" ]]; then
    echo "ERROR: Requirements file not found: $REQ_FILE"
    exit 1
fi

echo "[1/5] Checking Python version"
python3 --version

echo "[2/5] Creating virtual environment"
if [[ ! -d "$VENV_DIR" ]]; then
    runuser -u linkticket -- python3 -m venv "$VENV_DIR"
fi

echo "[3/5] Installing dependencies"
runuser -u linkticket -- \
    "$VENV_DIR/bin/python" -m pip install \
    -r "$REQ_FILE"

echo "[4/5] Checking Django"
runuser -u linkticket -- \
    "$VENV_DIR/bin/python" -m django --version

echo "[5/5] Checking Gunicorn"
runuser -u linkticket -- \
    "$VENV_DIR/bin/gunicorn" --version

echo "Django environment setup completed."


#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/var/www/ticket_app"
SERVICE_NAME="linkticket-aws"
SERVICE_SOURCE="${APP_DIR}/scripts/was/linkticket-aws.service"
SERVICE_TARGET="/etc/systemd/system/${SERVICE_NAME}.service"
ENV_FILE="/etc/linkticket/linkticket.env"
GUNICORN_CONFIG="${APP_DIR}/scripts/was/gunicorn-aws.conf.py"
VENV_PYTHON="${APP_DIR}/.venv/bin/python"
VENV_GUNICORN="${APP_DIR}/.venv/bin/gunicorn"

echo "========================================"
echo " LINKTICKET AWS WAS Deployment"
echo "========================================"

# 1. Root permission
if [[ "$(id -u)" -ne 0 ]]; then
    echo "ERROR: Run this script as root."
    exit 1
fi

# 2. Verify application files
echo "[1/6] Checking application files"

for file in \
    "${APP_DIR}/manage.py" \
    "${APP_DIR}/config/wsgi.py" \
    "${APP_DIR}/config/settings_aws.py" \
    "${SERVICE_SOURCE}" \
    "${GUNICORN_CONFIG}" \
    "${VENV_PYTHON}" \
    "${VENV_GUNICORN}"
do
    if [[ ! -f "${file}" ]]; then
        echo "ERROR: Missing file: ${file}"
        exit 1
    fi
done

# 3. Verify service account
echo "[2/6] Checking service account"

if ! id linkticket &>/dev/null; then
    echo "ERROR: Service account 'linkticket' does not exist."
    exit 1
fi

# 4. Verify environment file
echo "[3/6] Checking environment configuration"

if [[ ! -f "${ENV_FILE}" ]]; then
    echo "ERROR: Missing environment file: ${ENV_FILE}"
    echo "Provision the environment file securely before deployment."
    exit 1
fi

if [[ ! -r "${ENV_FILE}" ]]; then
    echo "ERROR: Environment file is not readable."
    exit 1
fi

# 5. Install systemd unit
echo "[4/6] Installing systemd service"

install -o root -g root -m 0644 \
    "${SERVICE_SOURCE}" \
    "${SERVICE_TARGET}"

systemctl daemon-reload

# 6. Validate service configuration
echo "[5/6] Validating systemd unit"

systemd-analyze verify "${SERVICE_TARGET}"

# 7. Deployment preparation complete
echo "[6/6] Deployment preparation completed"

echo ""
echo "Service installed: ${SERVICE_NAME}"
echo "Django settings: config.settings_aws"
echo "Gunicorn port: 8082"
echo ""
echo "NOTICE:"
echo "The service has NOT been started."
echo "Verify RDS, Redis, EFS and Django settings first."
echo ""
echo "Next commands after dependencies are ready:"
echo "  systemctl enable ${SERVICE_NAME}"
echo "  systemctl start ${SERVICE_NAME}"
echo "  systemctl status ${SERVICE_NAME}"

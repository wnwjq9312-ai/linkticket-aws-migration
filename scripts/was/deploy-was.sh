
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

# Verify environment file permissions
ENV_MODE="$(stat -c '%a' "${ENV_FILE}")"

if [[ "${ENV_MODE}" != "600" && "${ENV_MODE}" != "640" ]]; then
    echo "ERROR: Insecure environment file permissions."
    echo "Expected permissions: 600 or 640"
    echo "Current permissions: ${ENV_MODE}"
    exit 1
fi

# Verify environment file owner
ENV_OWNER="$(stat -c '%U' "${ENV_FILE}")"

if [[ "${ENV_OWNER}" != "root" ]]; then
    echo "ERROR: Environment file must be owned by root."
    exit 1
fi

# Required AWS WAS environment variables
required_vars=(
    DJANGO_SECRET_KEY
    DJANGO_ALLOWED_HOSTS
    CSRF_TRUSTED_ORIGINS
    DB_ENGINE
    DB_HOST
    DB_PORT
    DB_NAME
    DB_USER
    DB_PASSWORD
    REDIS_URL
    STATIC_ROOT
    MEDIA_ROOT
    WEB_NFS_MOUNT
)

# Check required variables without printing secret values
for var in "${required_vars[@]}"; do
    line="$(grep -E "^${var}=" "${ENV_FILE}" | tail -n 1 || true)"

    if [[ -z "${line}" ]]; then
        echo "ERROR: Missing environment variable: ${var}"
        exit 1
    fi

    value="${line#*=}"

    if [[ -z "${value}" || "${value}" == *REPLACE_WITH_* ]]; then
        echo "ERROR: Invalid or placeholder value: ${var}"
        exit 1
    fi
done

# Verify database engine
DB_ENGINE_LINE="$(grep -E '^DB_ENGINE=' "${ENV_FILE}" | tail -n 1)"
DB_ENGINE_VALUE="${DB_ENGINE_LINE#*=}"

if [[ "${DB_ENGINE_VALUE}" != "mysql" ]]; then
    echo "ERROR: DB_ENGINE must be mysql for AWS deployment."
    exit 1
fi

# Verify Django secret key length
SECRET_LINE="$(grep -E '^DJANGO_SECRET_KEY=' "${ENV_FILE}" | tail -n 1)"
SECRET_VALUE="${SECRET_LINE#*=}"

if [[ ${#SECRET_VALUE} -lt 50 ]]; then
    echo "ERROR: DJANGO_SECRET_KEY must be at least 50 characters."
    exit 1
fi

echo "Environment configuration validation passed."

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

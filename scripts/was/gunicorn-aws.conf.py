
import os

# LINKTICKET AWS Gunicorn Configuration
# WEB Nginx -> WAS Gunicorn :8082

bind = "0.0.0.0:8082"

workers = int(os.environ.get("GUNICORN_WORKERS", "2"))

timeout = 60

accesslog = "-"
errorlog = "-"
capture_output = True

# Trusted proxy IPs must be configured for the AWS WEB instances.
forwarded_allow_ips = os.environ.get(
    "GUNICORN_FORWARDED_ALLOW_IPS", ""
)

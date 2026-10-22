
"""LINKTICKET AWS production settings."""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

from .settings import *  # noqa: F403,F401


def required(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise ImproperlyConfigured(
            f"Missing AWS environment variable: {name}"
        )
    return value


def absolute_path(name):
    value = Path(required(name))
    if not value.is_absolute():
        raise ImproperlyConfigured(
            f"{name} must be an absolute path"
        )
    return value


DEBUG = False

SECRET_KEY = required("DJANGO_SECRET_KEY")
if (
    len(SECRET_KEY) < 50
    or len(set(SECRET_KEY)) < 5
    or SECRET_KEY.startswith("dev-")
):
    raise ImproperlyConfigured(
        "Use a randomly generated production SECRET_KEY"
    )

ALLOWED_HOSTS = [
    value.strip()
    for value in required("DJANGO_ALLOWED_HOSTS").split(",")
    if value.strip()
]

if not ALLOWED_HOSTS or "*" in ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "Wildcard ALLOWED_HOSTS is not permitted"
    )

CSRF_TRUSTED_ORIGINS = [
    value.strip()
    for value in required("CSRF_TRUSTED_ORIGINS").split(",")
    if value.strip()
]

if not CSRF_TRUSTED_ORIGINS or any(
    not origin.startswith("https://") or "*" in origin
    for origin in CSRF_TRUSTED_ORIGINS
):
    raise ImproperlyConfigured(
        "Explicit HTTPS CSRF origins are required"
    )

# RDS MariaDB connection
if os.environ.get("DB_ENGINE", "mysql") != "mysql":
    raise ImproperlyConfigured(
        "AWS production requires MariaDB/MySQL"
    )

db = DATABASES["default"]

if db["ENGINE"] != "django.db.backends.mysql":
    raise ImproperlyConfigured(
        "AWS production requires MySQL backend"
    )

required("DB_HOST")
required("DB_NAME")
required("DB_USER")
required("DB_PASSWORD")

if str(db["PORT"]) != "3306":
    raise ImproperlyConfigured(
        "AWS RDS must use port 3306"
    )

db["CONN_MAX_AGE"] = 60
db["CONN_HEALTH_CHECKS"] = True

# Shared file storage
STATIC_ROOT = absolute_path("STATIC_ROOT")
MEDIA_ROOT = absolute_path("MEDIA_ROOT")
WEB_NFS_MOUNT = str(absolute_path("WEB_NFS_MOUNT"))

NFT_UPLOADS_ENABLED = False
NFT_MEDIA_ROOT = None
NFT_NFS_MOUNT = None

MEDIA_URL = "/media/"

STORAGES = {
    "default": {
        "BACKEND": "common.storage.MountedStorage",
        "OPTIONS": {
            "location": MEDIA_ROOT,
            "base_url": MEDIA_URL,
            "mount_path": WEB_NFS_MOUNT,
        },
    },
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
        )
    },
}

# Shared Redis sessions
REDIS_URL = required("REDIS_URL")

from urllib.parse import urlsplit, urlunsplit

SESSION_REDIS_DB = int(
    os.environ.get("SESSION_REDIS_DB", "0")
)

if SESSION_REDIS_DB < 0:
    raise ImproperlyConfigured(
        "SESSION_REDIS_DB must be nonnegative"
    )

redis_parts = urlsplit(REDIS_URL)

SESSION_REDIS_URL = urlunsplit(
    redis_parts._replace(
        path=f"/{SESSION_REDIS_DB}",
        query=""
    )
)

CACHES = {
    "default": {
        "BACKEND": (
            "django.core.cache.backends.locmem.LocMemCache"
        )
    },
    "sessions": {
        "BACKEND": (
            "django.core.cache.backends.redis.RedisCache"
        ),
        "LOCATION": SESSION_REDIS_URL,
        "KEY_PREFIX": "linkticket:sessions",
        "OPTIONS": {
            "socket_connect_timeout": 5,
            "socket_timeout": 5,
        },
    },
}

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_CACHE_ALIAS = "sessions"

COLLECTIBLE_LINKS_ENABLED = False

# HTTPS via AWS ALB
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https"
)

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = int(
    os.environ.get("SECURE_HSTS_SECONDS", "0")
)

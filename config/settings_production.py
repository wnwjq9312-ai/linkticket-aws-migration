"""Manual on-premise deployment; never use development defaults in production."""
import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
from .settings import *  # noqa: F403


def required(name):
    value = os.environ.get(name, '').strip()
    if not value:
        raise ImproperlyConfigured('Missing production environment variable: ' + name)
    return value


def absolute_path(name):
    value = Path(required(name))
    if not value.is_absolute():
        raise ImproperlyConfigured(name + ' must be an absolute path')
    return value


DEBUG = False
SECRET_KEY = required('DJANGO_SECRET_KEY')
if len(SECRET_KEY) < 50 or len(set(SECRET_KEY)) < 5 or SECRET_KEY.startswith('dev-'):
    raise ImproperlyConfigured('Use a randomly generated production DJANGO_SECRET_KEY')
ALLOWED_HOSTS = [x.strip() for x in required('DJANGO_ALLOWED_HOSTS').split(',') if x.strip()]
if not ALLOWED_HOSTS or '*' in ALLOWED_HOSTS:
    raise ImproperlyConfigured('Wildcard ALLOWED_HOSTS is not permitted')
CSRF_TRUSTED_ORIGINS = [x.strip() for x in required('CSRF_TRUSTED_ORIGINS').split(',') if x.strip()]
if not CSRF_TRUSTED_ORIGINS or any(not x.startswith('https://') or '*' in x for x in CSRF_TRUSTED_ORIGINS):
    raise ImproperlyConfigured('Use explicit HTTPS CSRF origins')
db = DATABASES['default']
if (db['ENGINE'], db.get('HOST'), str(db.get('PORT')), db['NAME'], db.get('USER')) != (
    'django.db.backends.mysql', '10.10.2.5', '4006', 'ticketing_db', 'ticket_app'
):
    raise ImproperlyConfigured('Production database must use ticket_app / ticketing_db via MaxScale 10.10.2.5:4006')
required('DB_PASSWORD')
db['CONN_MAX_AGE'] = 60
db['CONN_HEALTH_CHECKS'] = True
STATIC_ROOT = absolute_path('STATIC_ROOT')
MEDIA_ROOT = absolute_path('MEDIA_ROOT')
NFT_UPLOADS_ENABLED = os.environ.get('NFT_UPLOADS_ENABLED', 'False').lower() == 'true'
NFT_MEDIA_ROOT = absolute_path('NFT_MEDIA_ROOT') if NFT_UPLOADS_ENABLED else None
WEB_NFS_MOUNT = str(absolute_path('WEB_NFS_MOUNT'))
NFT_NFS_MOUNT = str(absolute_path('NFT_NFS_MOUNT')) if NFT_UPLOADS_ENABLED else None
if NFT_UPLOADS_ENABLED and MEDIA_ROOT == NFT_MEDIA_ROOT:
    raise ImproperlyConfigured('General media and NFT storage must be separated')
MEDIA_URL = '/media/'
NFT_MEDIA_URL = os.environ.get('NFT_MEDIA_URL', '')
if NFT_UPLOADS_ENABLED and not NFT_MEDIA_URL:
    raise ImproperlyConfigured('NFT_MEDIA_URL is required for enabled NFT uploads')
STORAGES = {
    'default': {'BACKEND': 'common.storage.MountedStorage', 'OPTIONS': {
        'location': MEDIA_ROOT, 'base_url': MEDIA_URL, 'mount_path': WEB_NFS_MOUNT,
    }},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}
REDIS_URL = required('REDIS_URL')
from urllib.parse import urlsplit, urlunsplit
# General Redis clients may use different logical DBs. Authentication sessions
# must use the same DB on both WAS nodes, including cross-node logout deletion.
SESSION_REDIS_DB = int(os.environ.get('SESSION_REDIS_DB', '0'))
if SESSION_REDIS_DB < 0:
    raise ImproperlyConfigured('SESSION_REDIS_DB must be nonnegative')
_session_redis = urlsplit(REDIS_URL)
SESSION_REDIS_URL = urlunsplit(_session_redis._replace(path='/' + str(SESSION_REDIS_DB), query=''))
# Redis is shared by both WAS nodes; DB fallback preserves existing sessions.
CACHES = {
    'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'},
    'sessions': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': SESSION_REDIS_URL,
        'KEY_PREFIX': 'linkticket:sessions',
        'OPTIONS': {'socket_connect_timeout': 5, 'socket_timeout': 5},
    },
}
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'sessions'
# Existing production NFT relation columns are a separately tracked schema issue.
COLLECTIBLE_LINKS_ENABLED = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
# WEB overwrites this header; restrict direct WAS access to trusted WEB peers.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_CONTENT_TYPE_NOSNIFF = True
# Enable after validating TLS on the actual domain; do not preload by default.
SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', '0'))

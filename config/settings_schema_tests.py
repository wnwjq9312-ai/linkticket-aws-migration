"""Disposable model-contract tests only, not deployment or migration validation.

Existing migration files describe the old development schema. Never use this
module for an application server or to adopt the production database.
"""
import os
import sys
from django.core.exceptions import ImproperlyConfigured

if 'test' not in sys.argv:
    raise ImproperlyConfigured('settings_schema_tests is only for manage.py test')
os.environ['DB_ENGINE'] = 'sqlite'
from .settings import *  # noqa: F403

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
MIGRATION_MODULES = {
    name: None for name in (
        'accounts', 'catalog', 'reservations', 'payments', 'tickets', 'coupons',
        'events', 'notices', 'admin', 'auth', 'contenttypes', 'sessions',
    )
}

"""Read-only model/schema evidence. Run on WAS after loading the protected env.

python deploy/inspect_database.py > schema-inspection.json
No DDL, migration application, passwords, or row data are emitted.
"""
import json
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_production')
import django
django.setup()
from django.apps import apps
from django.db import connection
from django.db.migrations.loader import MigrationLoader

report = {'models': {}, 'tables': {}, 'applied_migrations': []}
for model in apps.get_models():
    report['models'][model._meta.db_table] = [
        {'column': f.column, 'type': f.db_type(connection), 'null': f.null,
         'primary_key': f.primary_key, 'unique': f.unique, 'index': f.db_index,
         'related_table': f.remote_field.model._meta.db_table if f.remote_field else None}
        for f in model._meta.local_fields
    ]
with connection.cursor() as cursor:
    for table in connection.introspection.table_names(cursor):
        report['tables'][table] = {
            'columns': [row._asdict() for row in connection.introspection.get_table_description(cursor, table)],
            'constraints': connection.introspection.get_constraints(cursor, table),
        }
report['applied_migrations'] = sorted('/'.join(key) for key in MigrationLoader(connection).applied_migrations)
print(json.dumps(report, ensure_ascii=False, indent=2, default=str))

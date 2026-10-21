"""Create a new role account; never reset or promote an existing member."""
import getpass
import os
import stat
from pathlib import Path

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = 'Create a new ADMIN/STAFF with a hidden password prompt or protected password file.'

    def add_arguments(self, parser):
        parser.add_argument('--username', required=True)
        parser.add_argument('--email', required=True)
        parser.add_argument('--role', required=True, choices=['ADMIN', 'STAFF'])
        parser.add_argument('--name', default='')
        parser.add_argument('--password-file')

    def handle(self, *args, **options):
        model = get_user_model()
        if model.objects.filter(username=options['username']).exists():
            raise CommandError('Account already exists; no password or role was changed.')
        if options['password_file']:
            path = Path(options['password_file'])
            if os.name != 'nt' and stat.S_IMODE(path.stat().st_mode) & 0o077:
                raise CommandError('Password file must not be accessible to group/other users.')
            password = path.read_text(encoding='utf-8').rstrip('\r\n')
        else:
            password = getpass.getpass('Initial password: ')
            if password != getpass.getpass('Confirm password: '):
                raise CommandError('Passwords do not match.')
        user = model(username=options['username'], email=options['email'])
        try:
            validate_password(password, user=user)
            with transaction.atomic():
                model.objects.create_user(
                    username=options['username'], email=options['email'], password=password,
                    first_name=options['name'], role=options['role'],
                )
        except ValidationError as exc:
            raise CommandError('Account validation failed; check input and uniqueness.') from exc
        finally:
            password = None
        self.stdout.write(self.style.SUCCESS('New role account created. Password is not displayed.'))

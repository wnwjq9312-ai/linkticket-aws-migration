import tempfile
from pathlib import Path
from unittest.mock import patch
from django.test import SimpleTestCase, override_settings
from django.core.files.base import ContentFile
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import default_storage
from common.storage import nft_storage, MountedStorage


class SharedSessionConfigurationTests(SimpleTestCase):
    def test_different_general_redis_databases_share_session_database(self):
        import json
        import os
        import secrets
        import subprocess
        import sys
        root = Path(__file__).resolve().parents[1]
        env = dict(os.environ, DJANGO_SECRET_KEY=secrets.token_urlsafe(48),
                   DJANGO_ALLOWED_HOSTS='www.linkticket.com',
                   CSRF_TRUSTED_ORIGINS='https://www.linkticket.com',
                   DB_ENGINE='mysql', DB_HOST='10.10.2.5', DB_PORT='4006',
                   DB_NAME='ticketing_db', DB_USER='ticket_app', DB_PASSWORD='test-only',
                   STATIC_ROOT=str(root/'staticfiles'), MEDIA_ROOT=str(root/'media'),
                   WEB_NFS_MOUNT=str(root), NFT_UPLOADS_ENABLED='False', SESSION_REDIS_DB='0')
        code = ('import json;from config import settings_production as s;'
                'from urllib.parse import urlsplit;'
                'print(json.dumps([s.SESSION_ENGINE, s.SESSION_CACHE_ALIAS,'
                'urlsplit(s.CACHES["sessions"]["LOCATION"]).path,'
                's.CACHES["sessions"]["KEY_PREFIX"]]))')
        results = []
        for database in (0, 1):
            env['REDIS_URL'] = f'redis://10.10.2.6:6379/{database}'
            result = subprocess.run([sys.executable,'-c',code],cwd=root,env=env,
                                    capture_output=True,text=True,check=True)
            results.append(json.loads(result.stdout))
        self.assertEqual(results[0], results[1])
        self.assertEqual(results[0], ['django.contrib.sessions.backends.cached_db',
                                     'sessions','/0','linkticket:sessions'])


class StorageDeploymentTests(SimpleTestCase):
    @override_settings(NFT_UPLOADS_ENABLED=False, NFT_MEDIA_ROOT=None, NFT_NFS_MOUNT=None, NFT_MEDIA_URL='')
    def test_disabled_upload_does_not_fallback_to_general_storage(self):
        from common.storage import nft_image_url
        self.assertEqual(nft_image_url('nft/existing.png'), '')
        with self.assertRaises(ImproperlyConfigured):
            nft_storage()

    @override_settings(NFT_UPLOADS_ENABLED=False, NFT_MEDIA_ROOT=None, NFT_NFS_MOUNT=None, NFT_MEDIA_URL='/verified-nft/')
    def test_read_url_does_not_require_write_mount(self):
        from common.storage import nft_image_url
        self.assertEqual(nft_image_url('nft/existing.png'), '/verified-nft/nft/existing.png')

    def test_nft_and_general_media_are_separate(self):
        with tempfile.TemporaryDirectory() as folder:
            general = Path(folder) / 'general'
            nft = Path(folder) / 'collectibles'
            with override_settings(MEDIA_ROOT=general, NFT_MEDIA_ROOT=nft, NFT_MEDIA_URL='/nft-media/'):
                name = nft_storage().save('nft/example.png', ContentFile(b'fixture'))
                self.assertTrue((nft / name).exists())
                self.assertFalse((general / name).exists())
                self.assertEqual(nft_storage().url(name), '/nft-media/nft/example.png')
                ordinary = default_storage.save('events/example.png', ContentFile(b'fixture'))
                self.assertTrue((general / ordinary).exists())

    def test_missing_mount_rejects_write(self):
        with tempfile.TemporaryDirectory() as folder:
            storage = MountedStorage(location=folder, mount_path=folder)
            with patch('common.storage.os.path.ismount', return_value=False):
                with self.assertRaises(ImproperlyConfigured):
                    storage.save('nft/test.png', ContentFile(b'fixture'))
            self.assertEqual(list(Path(folder).iterdir()), [])

    def test_storage_outside_mount_rejects_write(self):
        with tempfile.TemporaryDirectory() as folder:
            storage = MountedStorage(location=Path(folder) / 'outside', mount_path=Path(folder) / 'mount')
            with patch('common.storage.os.path.ismount', return_value=True):
                with self.assertRaises(ImproperlyConfigured):
                    storage.save('test.png', ContentFile(b'fixture'))

    def test_development_keeps_existing_relative_paths(self):
        with tempfile.TemporaryDirectory() as folder, override_settings(MEDIA_ROOT=folder, NFT_MEDIA_ROOT=None, NFT_MEDIA_URL='/media/'):
            name = nft_storage().save('nft/old.png', ContentFile(b'fixture'))
            self.assertTrue((Path(folder) / name).exists())
            self.assertEqual(nft_storage().url(name), '/media/nft/old.png')

"""Keep stored NFT relative paths stable while separating physical storage."""
import os
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import FileSystemStorage


class MountedStorage(FileSystemStorage):
    def __init__(self, *args, mount_path=None, **kwargs):
        self.mount_path = mount_path
        super().__init__(*args, **kwargs)

    def _save(self, name, content):
        # Do not silently fill a local disk when the required NFS is absent.
        if self.mount_path:
            mount = Path(self.mount_path).resolve()
            root = Path(self.location).resolve()
            if not os.path.ismount(mount) or (root != mount and mount not in root.parents):
                raise ImproperlyConfigured('Required media mount is unavailable or storage is outside it.')
        return super()._save(name, content)


def nft_image_url(name):
    # Resolving an existing URL must not require an upload mount.
    if name and name.startswith('/nft_images/') and '..' not in Path(name).parts:
        from urllib.parse import quote
        return quote(name, safe='/')
    if not name or not settings.NFT_MEDIA_URL or name.startswith(('http:', 'https:', '/')):
        return ''
    return FileSystemStorage(base_url=settings.NFT_MEDIA_URL).url(name)


def nft_storage():
    if not settings.NFT_UPLOADS_ENABLED:
        raise ImproperlyConfigured('NFT uploads are disabled')
    # Construct per use so override_settings and development defaults remain valid.
    return MountedStorage(
        location=settings.NFT_MEDIA_ROOT or settings.MEDIA_ROOT,
        base_url=settings.NFT_MEDIA_URL,
        mount_path=getattr(settings, 'NFT_NFS_MOUNT', None),
    )

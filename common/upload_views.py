import mimetypes
from pathlib import Path
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404


def image_response(root, name, private=False):
    root = Path(root).resolve()
    target = (root / name).resolve()
    if root not in target.parents or target.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.webp', '.gif') or not target.is_file():
        raise Http404
    response = FileResponse(target.open('rb'), content_type=mimetypes.guess_type(str(target))[0] or 'application/octet-stream')
    response['X-Content-Type-Options'] = 'nosniff'
    response['Cache-Control'] = 'private, no-store' if private else 'public, max-age=300'
    return response


def media_image(request, name):
    if name.split('/')[0] not in ('performances', 'notices', 'events'):
        raise Http404
    return image_response(settings.MEDIA_ROOT, name)


@login_required
def nft_image(request, name):
    from events.ui_views import visible_collectibles
    if not visible_collectibles(request.user).filter(image_path='/nft_images/' + name).exists():
        raise Http404
    return image_response(settings.NFT_MEDIA_ROOT, name, private=True)

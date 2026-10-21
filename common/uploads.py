from django.core.exceptions import ValidationError
from PIL import Image

def validate_ui_image(value):
    if not value:
        return
    if value.size > 5 * 1024 * 1024:
        raise ValidationError('이미지는 5MB 이하여야 합니다.')
    try:
        image = Image.open(value)
        if image.format not in ('PNG', 'JPEG', 'WEBP'):
            raise ValidationError('PNG, JPEG, WebP 이미지만 사용할 수 있습니다.')
        image.verify()
    except ValidationError:
        raise
    except Exception:
        raise ValidationError('올바른 이미지 파일을 선택해주세요.')
    finally:
        value.seek(0)

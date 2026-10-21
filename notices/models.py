"""
참조: 개발 기능 명세서 v2.0 3.2절(notice)
"""
from django.db import models
from common.uploads import validate_ui_image

from accounts.models import Member


class NoticeType(models.TextChoices):
    """v2.3 수정본 13.6절 추가."""

    # Existing MariaDB chk_notice_type stores Korean labels, not API codes.
    NOTICE = "공지", "공지"
    EVENT = "이벤트", "이벤트"
    GUIDE = "안내", "안내"
    MAINTENANCE = "점검", "점검"


class Notice(models.Model):
    notice_id = models.AutoField(primary_key=True)
    notice_type = models.CharField(max_length=20, choices=NoticeType.choices, default=NoticeType.NOTICE)
    author = models.ForeignKey(Member, on_delete=models.PROTECT, db_column="author_id")
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to="notices/", blank=True, validators=[validate_ui_image])
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    view_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "notice"

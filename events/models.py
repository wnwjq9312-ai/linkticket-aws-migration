"""
참조: 개발 기능 명세서 v2.0 3.2절(event, event_reward, digital_collectible), 10장
"""
from django.db import models
from common.uploads import validate_ui_image

from accounts.models import Member
from catalog.models import Performance
from reservations.models import Reservation


class EventStatus(models.TextChoices):
    SCHEDULED = "SCHEDULED", "예정"
    ACTIVE = "ACTIVE", "진행 중"
    ENDED = "ENDED", "종료"
    CANCELLED = "CANCELLED", "취소"


class EventRewardType(models.TextChoices):
    COUPON = "COUPON", "쿠폰"
    DIGITAL_COLLECTIBLE = "DIGITAL_COLLECTIBLE", "디지털 컬렉터블"
    DONATION_POINT = "DONATION_POINT", "기부 포인트"
    TICKET_SUPPORT = "TICKET_SUPPORT", "티켓 지원"


class CollectibleStatus(models.TextChoices):
    PENDING = "PENDING", "발급 대기"
    ISSUED = "ISSUED", "발급 완료"
    FAILED = "FAILED", "발급 실패"
    REVOKED = "REVOKED", "회수"


class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    performance = models.ForeignKey(Performance, on_delete=models.CASCADE, db_column="performance_id")
    event_name = models.CharField(max_length=100)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to="events/", blank=True, validators=[validate_ui_image])
    event_type = models.CharField(max_length=20)
    event_start = models.DateTimeField()
    event_end = models.DateTimeField()
    event_status = models.CharField(max_length=20, choices=EventStatus.choices, default=EventStatus.SCHEDULED)

    class Meta:
        db_table = "event"


class EventReward(models.Model):
    reward_id = models.AutoField(primary_key=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, db_column="event_id")
    member = models.ForeignKey(Member, on_delete=models.CASCADE, db_column="member_id")
    reward_type = models.CharField(max_length=30, choices=EventRewardType.choices)
    reward_value = models.CharField(max_length=255, null=True, blank=True)
    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "event_reward"
        constraints = [
            models.UniqueConstraint(fields=["event", "member", "reward_type"], name="uniq_event_member_reward_type")
        ]


class DigitalCollectible(models.Model):
    collectible_id = models.AutoField(primary_key=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, db_column="member_id")
    performance = models.ForeignKey(Performance, on_delete=models.CASCADE, db_column="performance_id")
    source_event = models.ForeignKey(
        Event, on_delete=models.SET_NULL, null=True, blank=True, db_column="source_event_id"
    )
    source_reservation = models.ForeignKey(
        Reservation, on_delete=models.SET_NULL, null=True, blank=True, db_column="source_reservation_id"
    )
    source_ticket = models.ForeignKey("tickets.Ticket", on_delete=models.SET_NULL, null=True, blank=True, related_name="collectibles")
    collectible_name = models.CharField(max_length=150)
    collectible_code = models.CharField(max_length=100, unique=True)
    image_path = models.CharField(max_length=255, blank=True)
    metadata_url = models.CharField(max_length=255, blank=True)
    collectible_status = models.CharField(
        max_length=20, choices=CollectibleStatus.choices, default=CollectibleStatus.PENDING
    )
    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "digital_collectible"


class CollectibleFavorite(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='nft_favorites')
    collectible = models.ForeignKey(DigitalCollectible, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'collectible_favorite'
        constraints = [models.UniqueConstraint(fields=['member', 'collectible'], name='uniq_member_collectible_favorite')]


class NftItem(models.Model):
    """Map the existing NFT inventory without altering its schema or logical paths."""
    nft_id = models.AutoField(primary_key=True)
    member = models.ForeignKey(Member, on_delete=models.PROTECT, null=True, blank=True)
    performance = models.ForeignKey(Performance, on_delete=models.PROTECT, null=True, blank=True)
    artist_name = models.CharField(max_length=100)
    nft_name = models.CharField(max_length=150)
    image_path = models.CharField(max_length=255)
    token_id = models.CharField(max_length=100, unique=True)
    metadata_url = models.CharField(max_length=255, null=True, blank=True)
    nft_status = models.CharField(max_length=20, choices=CollectibleStatus.choices, default=CollectibleStatus.ISSUED)
    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'nft_item'

    @property
    def collectible_name(self):
        return self.nft_name

    @property
    def collectible_code(self):
        return self.token_id

    @property
    def collectible_status(self):
        return self.nft_status

    def get_collectible_status_display(self):
        return self.get_nft_status_display()

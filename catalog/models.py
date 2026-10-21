"""
참조: 개발 기능 명세서 v2.0 3.2절(performance, performance_schedule, seat)
"""
from django.db import models
from common.uploads import validate_ui_image
from common.db_fields import PerformanceGenreField


class PerformanceStatus(models.TextChoices):
    DRAFT = "DRAFT", "등록 중"
    PUBLISHED = "PUBLISHED", "공개"
    CANCELLED = "CANCELLED", "취소"
    COMPLETED = "COMPLETED", "종료"


class SaleStatus(models.TextChoices):
    UPCOMING = "UPCOMING", "예매 예정"
    OPEN = "OPEN", "예매 가능"
    SOLD_OUT = "SOLD_OUT", "매진"
    CLOSED = "CLOSED", "예매 종료"
    CANCELLED = "CANCELLED", "회차 취소"


class SeatStatus(models.TextChoices):
    AVAILABLE = "AVAILABLE", "예매 가능"
    RESERVED = "RESERVED", "예매 완료"
    BLOCKED = "BLOCKED", "판매 불가"


class PerformanceGenre(models.TextChoices):
    """v2.3 수정본 13.1-1절 추가."""

    CONCERT = "CONCERT", "콘서트"
    MUSICAL = "MUSICAL", "뮤지컬"
    FESTIVAL = "FESTIVAL", "페스티벌"
    PLAY = "PLAY", "연극"
    CLASSICAL = "CLASSICAL", "클래식"
    FANMEETING = "FANMEETING", "팬미팅"
    EXHIBITION_ETC = "EXHIBITION_ETC", "전시/기타"


class Performance(models.Model):
    performance_id = models.AutoField(primary_key=True)
    performance_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="performances/", blank=True, null=True, validators=[validate_ui_image])
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    venue_name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    base_price = models.IntegerField()
    total_seats = models.IntegerField()
    performance_status = models.CharField(
        max_length=20, choices=PerformanceStatus.choices, default=PerformanceStatus.DRAFT
    )
    genre = PerformanceGenreField(max_length=20, choices=PerformanceGenre.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = "performance"

    def __str__(self):
        return self.performance_name


class PerformanceSchedule(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    performance = models.ForeignKey(
        Performance, on_delete=models.CASCADE, db_column="performance_id", related_name="schedules"
    )
    performance_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    sale_status = models.CharField(max_length=20, choices=SaleStatus.choices, default=SaleStatus.UPCOMING)
    sale_start_at = models.DateTimeField()
    sale_end_at = models.DateTimeField()

    class Meta:
        db_table = "performance_schedule"
        constraints = [
            models.UniqueConstraint(
                fields=["performance", "performance_date", "start_time"],
                name="uniq_performance_schedule_slot",
            )
        ]


class Seat(models.Model):
    seat_id = models.AutoField(primary_key=True)
    schedule = models.ForeignKey(
        PerformanceSchedule, on_delete=models.CASCADE, db_column="schedule_id", related_name="seats"
    )
    seat_number = models.CharField(max_length=10)
    seat_grade = models.CharField(max_length=20)
    seat_price = models.IntegerField()
    seat_status = models.CharField(max_length=20, choices=SeatStatus.choices, default=SeatStatus.AVAILABLE)

    class Meta:
        db_table = "seat"
        constraints = [
            models.UniqueConstraint(fields=["schedule", "seat_number"], name="uniq_seat_schedule_number")
        ]

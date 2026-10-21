"""
참조: 개발 기능 명세서 v2.0 3.2절(reservation, reservation_seat)
"""
from django.db import models

from accounts.models import Member
from catalog.models import PerformanceSchedule, Seat


class ReservationStatus(models.TextChoices):
    PENDING_PAYMENT = "PENDING_PAYMENT", "결제 대기"
    CONFIRMED = "CONFIRMED", "예매 확정"
    CANCELLED = "CANCELLED", "취소"
    EXPIRED = "EXPIRED", "시간 초과"
    REFUNDED = "REFUNDED", "환불 완료"


class Reservation(models.Model):
    reservation_id = models.AutoField(primary_key=True)
    member = models.ForeignKey(Member, on_delete=models.PROTECT, db_column="member_id", related_name="reservations")
    schedule = models.ForeignKey(PerformanceSchedule, on_delete=models.PROTECT, db_column="schedule_id")
    reservation_code = models.CharField(max_length=50, unique=True)
    reservation_time = models.DateTimeField(auto_now_add=True)
    total_amount = models.IntegerField()
    reservation_status = models.CharField(
        max_length=20, choices=ReservationStatus.choices, default=ReservationStatus.PENDING_PAYMENT
    )
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = "reservation"


class ReservationSeat(models.Model):
    reservation_seat_id = models.AutoField(primary_key=True)
    reservation = models.ForeignKey(
        Reservation, on_delete=models.CASCADE, db_column="reservation_id", related_name="reservation_seats"
    )
    seat = models.ForeignKey(Seat, on_delete=models.PROTECT, db_column="seat_id")
    price = models.IntegerField()

    class Meta:
        db_table = "reservation_seat"
        # 명세서 3.1-13절: DB 레벨 UNIQUE(seat_id)는 두지 않는다. 동시성 제어는
        # catalog.services(Redis Lock) + payments.services(select_for_update())로 보장한다.

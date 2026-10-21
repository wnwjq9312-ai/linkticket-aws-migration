"""
참조: 개발 기능 명세서 v2.0 3.2절(ticket)
"""
from django.db import models

from accounts.models import Member
from reservations.models import ReservationSeat


class TicketStatus(models.TextChoices):
    ISSUED = "ISSUED", "사용 가능"
    USED = "USED", "사용 완료"
    CANCELLED = "CANCELLED", "취소"
    EXPIRED = "EXPIRED", "만료"
    BLOCKED = "BLOCKED", "사용 정지"


class Ticket(models.Model):
    ticket_id = models.AutoField(primary_key=True)
    reservation_seat = models.OneToOneField(
        ReservationSeat, on_delete=models.PROTECT, db_column="reservation_seat_id"
    )
    ticket_code = models.CharField(max_length=50, unique=True)
    qr_token_hash = models.CharField(max_length=255, unique=True)
    ticket_status = models.CharField(max_length=20, choices=TicketStatus.choices, default=TicketStatus.ISSUED)
    issued_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    checked_by = models.ForeignKey(
        Member, on_delete=models.SET_NULL, null=True, blank=True, db_column="checked_by",
        related_name="checked_tickets",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ticket"

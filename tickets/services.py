"""
참조: 개발 기능 명세서 v2.0 7장(티켓 발급 및 QR 검증)
"""
import hashlib
import secrets
import uuid

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from common.exceptions import TicketAlreadyUsed, TicketBlocked, TicketCancelled, TicketExpired

from .models import Ticket, TicketStatus


def _hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode()).hexdigest()


def generate_ticket_code() -> str:
    return f"TKT-{uuid.uuid4().hex[:10].upper()}"


def issue_ticket(reservation_seat):
    """
    7.1절: payment=PAID, reservation=CONFIRMED, seat=RESERVED 조건을 만족한 뒤 호출한다.
    반환값 (ticket, raw_token) 중 raw_token은 QR에 인코딩할 값이며 DB에는 저장하지 않는다(7.3절).
    """
    raw_token = secrets.token_urlsafe(32)
    ticket = Ticket.objects.create(
        reservation_seat=reservation_seat,
        ticket_code=generate_ticket_code(),
        qr_token_hash=_hash_token(raw_token),
        ticket_status=TicketStatus.ISSUED,
        expires_at=None,  # 18장 체크리스트: QR Token 만료 정책 팀 확정 필요
    )
    return ticket, raw_token


@transaction.atomic
def verify_ticket(raw_token: str, staff_member) -> Ticket:
    """7.3~7.4절: QR 검증 + USED 변경을 하나의 트랜잭션으로 처리한다."""
    token_hash = _hash_token(raw_token)
    ticket = get_object_or_404(Ticket.objects.select_for_update(), qr_token_hash=token_hash)

    if ticket.ticket_status == TicketStatus.USED:
        raise TicketAlreadyUsed()
    if ticket.ticket_status == TicketStatus.CANCELLED:
        raise TicketCancelled()
    if ticket.ticket_status == TicketStatus.BLOCKED:
        raise TicketBlocked()
    if ticket.ticket_status == TicketStatus.EXPIRED or (ticket.expires_at and timezone.now() > ticket.expires_at):
        ticket.ticket_status = TicketStatus.EXPIRED
        ticket.save(update_fields=["ticket_status", "updated_at"])
        raise TicketExpired()

    ticket.ticket_status = TicketStatus.USED
    ticket.used_at = timezone.now()
    ticket.checked_by = staff_member
    ticket.save(update_fields=["ticket_status", "used_at", "checked_by", "updated_at"])
    return ticket


def cancel_tickets_for_reservation(reservation) -> None:
    """8장: 예매 취소/환불 시 해당 예매의 모든 티켓을 CANCELLED 처리한다."""
    Ticket.objects.filter(reservation_seat__reservation=reservation).update(
        ticket_status=TicketStatus.CANCELLED
    )

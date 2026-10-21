"""
참조: 4장(전체 예매 업무 흐름), 5.1절, 8장(예매 취소/환불)
"""
import uuid

from django.db import transaction
from django.utils import timezone

from catalog import services as catalog_services
from catalog.models import Seat, SeatStatus
from common.exceptions import SeatAlreadyHeld

from .models import Reservation, ReservationSeat, ReservationStatus


def generate_reservation_code() -> str:
    """외부 노출용 예매번호 (3.2절 reservation_code UNIQUE). 형식은 18장 팀 확정 필요."""
    return f"RSV-{uuid.uuid4().hex[:10].upper()}"


@transaction.atomic
def create_reservation(member, schedule_id: int, seat_ids: list) -> Reservation:
    """
    4장 흐름: 좌석이 Redis에 이미 선점(hold_seat)되어 있어야 호출 가능하다.
    선점되어 있지 않은 좌석이 하나라도 있으면 SeatAlreadyHeld를 발생시킨다.
    """
    for seat_id in seat_ids:
        if not catalog_services.is_seat_held_by(member.member_id, schedule_id, seat_id):
            raise SeatAlreadyHeld("좌석 선점이 만료되었거나 존재하지 않습니다. 다시 선택해주세요.")

    seats = list(Seat.objects.filter(pk__in=seat_ids, schedule_id=schedule_id))
    total_amount = sum(seat.seat_price for seat in seats)

    reservation = Reservation.objects.create(
        member=member,
        schedule_id=schedule_id,
        reservation_code=generate_reservation_code(),
        total_amount=total_amount,
        reservation_status=ReservationStatus.PENDING_PAYMENT,
    )
    ReservationSeat.objects.bulk_create(
        [ReservationSeat(reservation=reservation, seat=seat, price=seat.seat_price) for seat in seats]
    )
    return reservation


@transaction.atomic
def cancel_reservation(reservation: Reservation, allow_seat_resale: bool) -> None:
    """8장: 예매 취소. 결제 환불 처리는 payments.services.refund_payment()에서 함께 호출한다."""
    reservation.reservation_status = ReservationStatus.CANCELLED
    reservation.save(update_fields=["reservation_status", "updated_at"])

    if allow_seat_resale:
        seat_ids = reservation.reservation_seats.values_list("seat_id", flat=True)
        Seat.objects.filter(pk__in=seat_ids).update(seat_status=SeatStatus.AVAILABLE)


def count_reserving_members(schedule_id: int) -> int:
    """8장 관리자 대시보드: 해당 회차를 예매한 서로 다른 회원 수(취소/만료/환불 제외)."""
    return (
        Reservation.objects.filter(schedule_id=schedule_id)
        .exclude(
            reservation_status__in=[
                ReservationStatus.CANCELLED,
                ReservationStatus.EXPIRED,
                ReservationStatus.REFUNDED,
            ]
        )
        .values("member_id")
        .distinct()
        .count()
    )


def count_confirmed_reservations(schedule_id: int) -> int:
    """8장 관리자 대시보드: 해당 회차의 확정 예매 건수."""
    return Reservation.objects.filter(schedule_id=schedule_id, reservation_status=ReservationStatus.CONFIRMED).count()


def count_todays_confirmed_reservations() -> int:
    """8장 관리자 대시보드: 오늘 확정된 전체 예매 건수."""
    today = timezone.localdate()
    return Reservation.objects.filter(
        reservation_time__date=today, reservation_status=ReservationStatus.CONFIRMED
    ).count()

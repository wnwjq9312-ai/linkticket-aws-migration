"""
참조: 5.2절(좌석 확정 시 트랜잭션), 6장 흐름, 7.1절(티켓 발급 시점),
      9.2절(쿠폰 사용 시점), 12.2절(트랜잭션 범위 기준), 8장(환불)

confirm_payment() / refund_payment()는 이 프로젝트에서 가장 중요한 함수다.
결제/좌석/티켓/쿠폰 상태를 하나의 트랜잭션으로 묶는 지점이므로 시그니처와
로직 순서를 임의로 바꾸지 않는다.
"""
import uuid

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from catalog.models import Seat, SeatStatus
from common.exceptions import PaymentFailed, SeatAlreadyReserved
from coupons import services as coupon_services
from reservations.models import Reservation, ReservationStatus
from tickets import services as ticket_services

from .models import Payment, PaymentStatus


def generate_transaction_id() -> str:
    return f"TXN-{uuid.uuid4().hex[:12].upper()}"


@transaction.atomic
def confirm_payment(reservation: Reservation, payment_method: str, coupon=None) -> Payment:
    """
    5.2절 권장 처리를 그대로 따른다: select_for_update()로 좌석을 잠그고
    seat/reservation/payment/ticket을 하나의 트랜잭션으로 확정한다.
    쿠폰이 있으면 결제 성공 시점에만 USED로 변경한다(9.2절).
    """
    reservation_seats = list(reservation.reservation_seats.select_for_update().select_related("seat"))

    for rs in reservation_seats:
        if rs.seat.seat_status != SeatStatus.AVAILABLE:
            raise SeatAlreadyReserved()

    total_amount = reservation.total_amount
    if coupon is not None:
        total_amount = max(0, total_amount - coupon.discount_amount)

    payment = Payment.objects.create(
        reservation=reservation,
        transaction_id=generate_transaction_id(),
        payment_method=payment_method,
        payment_amount=total_amount,
        payment_status=PaymentStatus.PENDING,
    )

    payment_succeeded = _charge(payment)  # 실제 PG 연동 지점(18장: Mock 처리 여부 팀 확정)

    if not payment_succeeded:
        payment.payment_status = PaymentStatus.FAILED
        payment.failed_at = timezone.now()
        payment.save(update_fields=["payment_status", "failed_at", "updated_at"])

        reservation.reservation_status = ReservationStatus.CANCELLED
        reservation.save(update_fields=["reservation_status", "updated_at"])
        raise PaymentFailed()

    for rs in reservation_seats:
        rs.seat.seat_status = SeatStatus.RESERVED
        rs.seat.save(update_fields=["seat_status"])

    reservation.reservation_status = ReservationStatus.CONFIRMED
    reservation.save(update_fields=["reservation_status", "updated_at"])

    payment.payment_status = PaymentStatus.PAID
    payment.paid_at = timezone.now()
    payment.save(update_fields=["payment_status", "paid_at", "updated_at"])

    if coupon is not None:
        coupon_services.consume_coupon(coupon, reservation)

    for rs in reservation_seats:
        ticket_services.issue_ticket(rs)

    return payment


def _charge(payment: Payment) -> bool:
    """실제 PG(결제대행사) 연동 지점. 18장 체크리스트: Mock 처리 여부 확정 전까지 항상 성공 처리한다."""
    return True


@transaction.atomic
def refund_payment(payment: Payment, allow_seat_resale: bool = False) -> None:
    """8장: 예매 취소/환불. payment/reservation/ticket/seat을 하나의 트랜잭션으로 변경한다."""
    payment.payment_status = PaymentStatus.REFUNDED
    payment.refunded_at = timezone.now()
    payment.save(update_fields=["payment_status", "refunded_at", "updated_at"])

    reservation = payment.reservation
    reservation.reservation_status = ReservationStatus.REFUNDED
    reservation.save(update_fields=["reservation_status", "updated_at"])

    ticket_services.cancel_tickets_for_reservation(reservation)

    if allow_seat_resale:
        seat_ids = reservation.reservation_seats.values_list("seat_id", flat=True)
        Seat.objects.filter(pk__in=seat_ids).update(seat_status=SeatStatus.AVAILABLE)


def get_performance_revenue(performance_id: int) -> int:
    """8장 관리자 대시보드: 결제 완료(PAID) 기준 공연 누적 매출."""
    return (
        Payment.objects.filter(
            reservation__schedule__performance_id=performance_id,
            payment_status=PaymentStatus.PAID,
        ).aggregate(total=Sum("payment_amount"))["total"]
        or 0
    )


def get_total_revenue() -> int:
    """8장 관리자 대시보드: 전체 누적 매출(결제 완료 기준)."""
    return Payment.objects.filter(payment_status=PaymentStatus.PAID).aggregate(total=Sum("payment_amount"))[
        "total"
    ] or 0

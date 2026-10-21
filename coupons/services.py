"""
참조: 개발 기능 명세서 v2.0 9장(쿠폰 기능)
"""
from django.utils import timezone

from common.exceptions import CouponExpired, CouponInvalid

from .models import Coupon, CouponStatus


def validate_coupon(coupon: Coupon, member) -> None:
    """9.1절: 쿠폰 적용 전 검증. 결제 화면에서 쿠폰 선택 시 호출한다(상태 변경 없음)."""
    if coupon.member_id != member.member_id:
        raise CouponInvalid()
    if coupon.coupon_status != CouponStatus.AVAILABLE:
        raise CouponInvalid()
    if timezone.now() >= coupon.expires_at:
        raise CouponExpired()


def consume_coupon(coupon: Coupon, reservation) -> None:
    """9.2절: 결제 성공 시점에만 호출한다. payments.services.confirm_payment() 내부 전용."""
    coupon.coupon_status = CouponStatus.USED
    coupon.used_at = timezone.now()
    coupon.used_reservation = reservation
    coupon.save(update_fields=["coupon_status", "used_at", "used_reservation", "updated_at"])


def restore_coupon(coupon: Coupon) -> None:
    """9.2절: 결제 실패 시 AVAILABLE 유지. 환불 시 재발급 여부는 18장 팀 확정 사항이다."""
    if coupon.coupon_status == CouponStatus.USED:
        coupon.coupon_status = CouponStatus.AVAILABLE
        coupon.used_at = None
        coupon.used_reservation = None
        coupon.save(update_fields=["coupon_status", "used_at", "used_reservation", "updated_at"])

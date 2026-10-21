"""
LINKTICKET 공통 예외 클래스
참조: 개발 기능 명세서 v2.0 13.2절

모든 업무 예외는 LinkTicketError를 상속한다. 새 예외를 추가할 때는
error_codes.py에 코드 상수를 먼저 추가한 뒤 이 파일에 클래스를 추가한다.
"""
from . import error_codes as ec


class LinkTicketError(Exception):
    """모든 업무 예외의 베이스 클래스."""

    error_code: str = "UNKNOWN_ERROR"
    status_code: int = 400
    default_message: str = "처리할 수 없는 요청입니다."

    def __init__(self, message: str = None):
        self.message = message or self.default_message
        super().__init__(self.message)


class SeatAlreadyHeld(LinkTicketError):
    error_code = ec.SEAT_ALREADY_HELD
    status_code = ec.STATUS_CODE_MAP[ec.SEAT_ALREADY_HELD]
    default_message = "다른 사용자가 이미 선점한 좌석입니다."


class SeatAlreadyReserved(LinkTicketError):
    error_code = ec.SEAT_ALREADY_RESERVED
    status_code = ec.STATUS_CODE_MAP[ec.SEAT_ALREADY_RESERVED]
    default_message = "이미 예매가 완료된 좌석입니다."


class ReservationExpired(LinkTicketError):
    error_code = ec.RESERVATION_EXPIRED
    status_code = ec.STATUS_CODE_MAP[ec.RESERVATION_EXPIRED]
    default_message = "예매 제한시간이 초과되었습니다."


class PaymentFailed(LinkTicketError):
    error_code = ec.PAYMENT_FAILED
    status_code = ec.STATUS_CODE_MAP[ec.PAYMENT_FAILED]
    default_message = "결제에 실패했습니다."


class CouponInvalid(LinkTicketError):
    error_code = ec.COUPON_INVALID
    status_code = ec.STATUS_CODE_MAP[ec.COUPON_INVALID]
    default_message = "사용할 수 없는 쿠폰입니다."


class CouponExpired(LinkTicketError):
    error_code = ec.COUPON_EXPIRED
    status_code = ec.STATUS_CODE_MAP[ec.COUPON_EXPIRED]
    default_message = "만료된 쿠폰입니다."


class TicketAlreadyUsed(LinkTicketError):
    error_code = ec.TICKET_ALREADY_USED
    status_code = ec.STATUS_CODE_MAP[ec.TICKET_ALREADY_USED]
    default_message = "이미 입장 처리된 티켓입니다."


class TicketCancelled(LinkTicketError):
    error_code = ec.TICKET_CANCELLED
    status_code = ec.STATUS_CODE_MAP[ec.TICKET_CANCELLED]
    default_message = "취소된 티켓입니다."


class TicketExpired(LinkTicketError):
    error_code = ec.TICKET_EXPIRED
    status_code = ec.STATUS_CODE_MAP[ec.TICKET_EXPIRED]
    default_message = "만료된 티켓입니다."


class TicketBlocked(LinkTicketError):
    error_code = ec.TICKET_BLOCKED
    status_code = ec.STATUS_CODE_MAP[ec.TICKET_BLOCKED]
    default_message = "관리자에 의해 차단된 티켓입니다."


class PermissionDeniedError(LinkTicketError):
    error_code = ec.PERMISSION_DENIED
    status_code = ec.STATUS_CODE_MAP[ec.PERMISSION_DENIED]
    default_message = "권한이 없습니다."


class RateLimitExceeded(LinkTicketError):
    error_code = ec.RATE_LIMIT_EXCEEDED
    status_code = ec.STATUS_CODE_MAP[ec.RATE_LIMIT_EXCEEDED]
    default_message = "요청 횟수가 너무 많습니다. 잠시 후 다시 시도해주세요."


class PurchaseLimitExceeded(LinkTicketError):
    error_code = ec.PURCHASE_LIMIT_EXCEEDED
    status_code = ec.STATUS_CODE_MAP[ec.PURCHASE_LIMIT_EXCEEDED]
    default_message = "구매 가능 매수를 초과했습니다."


class SuspiciousClientBlocked(LinkTicketError):
    error_code = ec.SUSPICIOUS_CLIENT_BLOCKED
    status_code = ec.STATUS_CODE_MAP[ec.SUSPICIOUS_CLIENT_BLOCKED]
    default_message = "비정상적인 접근으로 차단되었습니다."

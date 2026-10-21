"""
참조: 개발 기능 명세서 v2.0 5.1절(좌석 임시 선점), 6.4절(레이트리밋)

이 파일의 함수 시그니처는 다른 개발자/AI가 그대로 사용해야 하는 계약이다.
별도 "네이밍 컨벤션 규칙" 문서의 함수 시그니처 계약표를 함께 참고한다.
"""
from django.db.models import Count

from common import redis_keys as rk
from common.exceptions import RateLimitExceeded, SeatAlreadyHeld, SeatAlreadyReserved
from common.redis_client import redis_client

from .models import Performance, PerformanceStatus, Seat, SeatStatus


def check_hold_rate_limit(client_ip: str, schedule_id: int) -> None:
    """6.4절: IP당 1분 좌석 선점 시도 횟수 제한."""
    key = rk.hold_rate_limit_key(client_ip=client_ip, schedule_id=schedule_id)
    count = redis_client.incr(key)
    if count == 1:
        redis_client.expire(key, rk.HOLD_RATE_LIMIT_TTL_SECONDS)
    if count > rk.HOLD_RATE_LIMIT_MAX_ATTEMPTS:
        raise RateLimitExceeded()


def hold_seat(member_id: int, schedule_id: int, seat_id: int, client_ip: str) -> None:
    """5.1절: Redis SET NX EX 300으로 좌석 임시 선점."""
    check_hold_rate_limit(client_ip, schedule_id)

    seat = Seat.objects.get(pk=seat_id, schedule_id=schedule_id)
    if seat.seat_status != SeatStatus.AVAILABLE:
        raise SeatAlreadyReserved()

    key = rk.seat_hold_key(schedule_id, seat_id)
    acquired = redis_client.set(key, member_id, nx=True, ex=rk.SEAT_HOLD_TTL_SECONDS)
    if not acquired:
        raise SeatAlreadyHeld()


def release_seat_hold(member_id: int, schedule_id: int, seat_id: int) -> None:
    """5.1절: 선점 해제 (DELETE /api/seats/{id}/hold/)."""
    key = rk.seat_hold_key(schedule_id, seat_id)
    held_by = redis_client.get(key)
    if held_by is not None and int(held_by) == member_id:
        redis_client.delete(key)


def is_seat_held_by(member_id: int, schedule_id: int, seat_id: int) -> bool:
    """4장: 예매 생성 시 이 좌석이 실제로 해당 회원에 의해 선점되어 있는지 확인."""
    key = rk.seat_hold_key(schedule_id, seat_id)
    held_by = redis_client.get(key)
    return held_by is not None and int(held_by) == member_id


def get_schedule_seat_stats(schedule_id: int) -> dict:
    """8장 관리자 대시보드: 회차별 좌석 상태 집계.
    반환: {"AVAILABLE": n, "RESERVED": n, "BLOCKED": n, "total": n}"""
    stats = {status: 0 for status in SeatStatus.values}
    rows = Seat.objects.filter(schedule_id=schedule_id).values("seat_status").annotate(count=Count("seat_id"))
    for row in rows:
        stats[row["seat_status"]] = row["count"]
    stats["total"] = sum(stats.values())
    return stats


def count_published_performances() -> int:
    """8장 대시보드: 현재 공개(PUBLISHED) 상태인 공연 수."""
    return Performance.objects.filter(performance_status=PerformanceStatus.PUBLISHED).count()


def get_total_unsold_seats() -> int:
    """8장 대시보드: 전체 공연 기준 미판매(AVAILABLE) 좌석 수."""
    return Seat.objects.filter(seat_status=SeatStatus.AVAILABLE).count()

"""
Redis 키 빌더 함수
참조: 개발 기능 명세서 v2.0 5.1절, 6.4절

모든 Redis 키는 이 모듈의 함수를 통해서만 생성한다. 다른 파일에서 f-string으로
직접 키를 조립하지 않는다 — 키 포맷이 바뀌어도 이 파일 하나만 고치면 되도록 한다.
"""


def seat_hold_key(schedule_id: int, seat_id: int) -> str:
    """5.1절: 좌석 임시 선점 키. TTL 300초."""
    return f"seat_hold:{schedule_id}:{seat_id}"


def hold_rate_limit_key(client_ip: str, schedule_id: int) -> str:
    """6.4절: IP별 좌석 선점 시도 횟수 제한 키. TTL 60초."""
    return f"rate:hold:{client_ip}:{schedule_id}"


def purchase_count_key(member_id: int, schedule_id: int) -> str:
    """6.4절: 회원별 회차당 구매 매수 제한 키."""
    return f"resv_count:{member_id}:{schedule_id}"


# 임계치 상수 — 18장 체크리스트: 팀에서 최종 확정 필요
SEAT_HOLD_TTL_SECONDS = 300
HOLD_RATE_LIMIT_TTL_SECONDS = 60
HOLD_RATE_LIMIT_MAX_ATTEMPTS = 10
MAX_TICKETS_PER_MEMBER_PER_SCHEDULE = 4

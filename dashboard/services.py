"""
참조: 관리자 페이지 모니터링 대시보드(신규) — 예매 인원 수, 미판매 좌석 수, 매출 집계

이 앱은 테이블을 소유하지 않는다. 집계 로직(카운트/합계)은 반드시 해당 데이터를
소유한 앱의 services.py 함수를 통해서만 가져온다 — catalog/reservations/payments의
모델을 이 파일에서 직접 집계 쿼리하지 않는다(2장 규칙의 read-전용 예외는 표시용
메타데이터 조회에만 해당하며, 집계는 예외 없이 소유 앱 services.py로 둔다).
"""
from catalog import services as catalog_services
from catalog.models import Performance, PerformanceSchedule
from payments import services as payment_services
from reservations import services as reservation_services


def get_overview_summary() -> dict:
    """관리자 대시보드 상단 KPI 카드 4개."""
    return {
        "published_performances": catalog_services.count_published_performances(),
        "today_confirmed_reservations": reservation_services.count_todays_confirmed_reservations(),
        "total_unsold_seats": catalog_services.get_total_unsold_seats(),
        "total_revenue": payment_services.get_total_revenue(),
    }


def get_schedule_dashboard(schedule: PerformanceSchedule) -> dict:
    """공연 상세 대시보드의 회차별 한 행."""
    seat_stats = catalog_services.get_schedule_seat_stats(schedule.schedule_id)
    return {
        "schedule_id": schedule.schedule_id,
        "performance_date": schedule.performance_date,
        "start_time": schedule.start_time,
        "sale_status": schedule.sale_status,
        "seat_stats": seat_stats,
        "reserving_members": reservation_services.count_reserving_members(schedule.schedule_id),
        "confirmed_reservations": reservation_services.count_confirmed_reservations(schedule.schedule_id),
    }


def get_performance_dashboard(performance_id: int) -> dict:
    """관리자 페이지 '공연별 상세' 화면: 회차별 예매 인원 / 좌석 판매 현황 / 누적 매출."""
    performance = Performance.objects.get(pk=performance_id)
    schedules = PerformanceSchedule.objects.filter(performance_id=performance_id).order_by(
        "performance_date", "start_time"
    )
    schedule_dashboards = [get_schedule_dashboard(s) for s in schedules]

    total_seats = sum(d["seat_stats"]["total"] for d in schedule_dashboards)
    total_reserved = sum(d["seat_stats"].get("RESERVED", 0) for d in schedule_dashboards)
    total_available = sum(d["seat_stats"].get("AVAILABLE", 0) for d in schedule_dashboards)

    return {
        "performance_id": performance_id,
        "performance_name": performance.performance_name,
        "performance_status": performance.performance_status,
        "schedules": schedule_dashboards,
        "total_seats": total_seats,
        "total_reserved": total_reserved,
        "total_available": total_available,
        "revenue": payment_services.get_performance_revenue(performance_id),
    }

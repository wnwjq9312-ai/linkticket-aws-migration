"""
참조: 관리자 페이지 모니터링 대시보드(신규) — ADMIN 전용
"""
from rest_framework.views import APIView

from common.permissions import IsAdmin
from common.response import success_response

from . import services


class AdminDashboardOverviewView(APIView):
    """GET /api/admin/dashboard/overview/ — 상단 KPI 카드(전체 요약)"""

    permission_classes = [IsAdmin]

    def get(self, request):
        return success_response(services.get_overview_summary())


class AdminDashboardPerformanceView(APIView):
    """GET /api/admin/dashboard/performances/{performance_id}/ — 공연별 회차/좌석/매출 상세"""

    permission_classes = [IsAdmin]

    def get(self, request, performance_id):
        return success_response(services.get_performance_dashboard(performance_id))

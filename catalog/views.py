"""
참조: 14.1~14.3절(공연 목록/상세/좌석 선택 화면)
"""
from rest_framework import generics, permissions
from rest_framework.views import APIView

from common.mixins import EnvelopeMixin
from common.permissions import IsStaffOrAdmin
from common.response import success_response

from . import services
from .models import Performance, PerformanceSchedule, Seat
from .serializers import (
    PerformanceDetailSerializer,
    PerformanceListSerializer,
    PerformanceScheduleSerializer,
    SeatSerializer,
)


class PerformanceListView(EnvelopeMixin, generics.ListAPIView):
    """GET /api/performances/ — 14.1절"""

    serializer_class = PerformanceListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Performance.objects.all()
        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(performance_status=status_param)
        return qs


class PerformanceDetailView(EnvelopeMixin, generics.RetrieveAPIView):
    """GET /api/performances/{id}/ — 14.2절"""

    queryset = Performance.objects.all()
    serializer_class = PerformanceDetailSerializer
    lookup_url_kwarg = "performance_id"
    lookup_field = "performance_id"
    permission_classes = [permissions.AllowAny]


class PerformanceScheduleListView(EnvelopeMixin, generics.ListAPIView):
    """GET /api/performances/{id}/schedules/ — 14.2절"""

    serializer_class = PerformanceScheduleSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return PerformanceSchedule.objects.filter(performance_id=self.kwargs["performance_id"])


class ScheduleSeatListView(EnvelopeMixin, generics.ListAPIView):
    """GET /api/schedules/{id}/seats/ — 14.3절"""

    serializer_class = SeatSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Seat.objects.filter(schedule_id=self.kwargs["schedule_id"])


class SeatHoldView(APIView):
    """POST/DELETE /api/seats/{id}/hold/ — 14.3절, 5.1절, 6.4절"""

    def post(self, request, seat_id):
        seat = Seat.objects.get(pk=seat_id)
        client_ip = request.META.get("REMOTE_ADDR", "")
        services.hold_seat(request.user.member_id, seat.schedule_id, seat_id, client_ip)
        return success_response({"seat_id": seat_id, "held_for_seconds": 300})

    def delete(self, request, seat_id):
        seat = Seat.objects.get(pk=seat_id)
        services.release_seat_hold(request.user.member_id, seat.schedule_id, seat_id)
        return success_response()


class StaffPerformanceCreateView(EnvelopeMixin, generics.CreateAPIView):
    """POST /api/staff/performances/ — 11.1절 공연 관리. STAFF/ADMIN 공용
    (직원 페이지 '공연 올리기')."""

    queryset = Performance.objects.all()
    serializer_class = PerformanceDetailSerializer
    permission_classes = [IsStaffOrAdmin]


class StaffPerformanceUpdateView(EnvelopeMixin, generics.UpdateAPIView):
    """PATCH /api/staff/performances/{id}/"""

    queryset = Performance.objects.all()
    serializer_class = PerformanceDetailSerializer
    lookup_url_kwarg = "performance_id"
    lookup_field = "performance_id"
    permission_classes = [IsStaffOrAdmin]


class StaffPerformanceScheduleCreateView(EnvelopeMixin, generics.CreateAPIView):
    """POST /api/staff/performances/{performance_id}/schedules/ — 회차 등록.
    공연은 회차가 하나 이상 있어야 좌석 판매가 가능하므로 '공연 올리기' 플로우의
    필수 다음 단계다."""

    serializer_class = PerformanceScheduleSerializer
    permission_classes = [IsStaffOrAdmin]

    def perform_create(self, serializer):
        serializer.save(performance_id=self.kwargs["performance_id"])


class StaffSeatBulkCreateView(APIView):
    """POST /api/staff/schedules/{schedule_id}/seats/ — 좌석 일괄 등록.
    요청 바디: {"seats": [{"seat_number": "A1", "seat_grade": "VIP", "seat_price": 150000}, ...]}"""

    permission_classes = [IsStaffOrAdmin]

    def post(self, request, schedule_id):
        seats_data = request.data.get("seats", [])
        for row in seats_data:
            row["schedule"] = schedule_id
        serializer = SeatSerializer(data=seats_data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(serializer.data, status=201)

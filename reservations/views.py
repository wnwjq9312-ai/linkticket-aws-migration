"""
참조: 14.3절, 14.5절, 14.6절
"""
from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView

from common.mixins import EnvelopeMixin
from common.permissions import IsAdmin
from common.response import success_response

from . import services
from .models import Reservation
from .serializers import ReservationCreateSerializer, ReservationDetailSerializer


class ReservationCreateView(APIView):
    """POST /api/reservations/ — 14.3절 '결제하기' 버튼"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ReservationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reservation = services.create_reservation(
            member=request.user,
            schedule_id=serializer.validated_data["schedule_id"],
            seat_ids=serializer.validated_data["seat_ids"],
        )
        return success_response(ReservationDetailSerializer(reservation).data, status=201)


class ReservationDetailView(EnvelopeMixin, generics.RetrieveAPIView):
    """GET /api/reservations/{id}/ — 14.4절, 14.5절"""

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        rows = Reservation.objects.all()
        return rows if self.request.user.is_superuser else rows.filter(member=self.request.user)
    serializer_class = ReservationDetailSerializer
    lookup_url_kwarg = "reservation_id"
    lookup_field = "reservation_id"


class ReservationListView(EnvelopeMixin, generics.ListAPIView):
    """GET /api/reservations/mine/ — 14.6절 마이페이지"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReservationDetailSerializer

    def get_queryset(self):
        return Reservation.objects.filter(member=self.request.user).order_by("-reservation_time")


class ReservationCancelView(APIView):
    """POST /api/reservations/{id}/cancel/ — 14.6절"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, reservation_id):
        reservation = get_object_or_404(Reservation,pk=reservation_id,member=request.user)
        services.cancel_reservation(reservation, allow_seat_resale=True)  # 18장: 재판매 정책 팀 확정 필요
        return success_response()


class AdminReservationListView(EnvelopeMixin, generics.ListAPIView):
    """GET /api/admin/reservations/ — 11.1절"""

    permission_classes = [IsAdmin]
    serializer_class = ReservationDetailSerializer

    def get_queryset(self):
        qs = Reservation.objects.all().order_by("-reservation_time")
        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(reservation_status=status_param)
        return qs

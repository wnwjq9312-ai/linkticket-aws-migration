"""
참조: 14.7절(디지털 티켓 QR), 14.8절(STAFF 검표 화면)
"""
from rest_framework import generics, permissions
from rest_framework.views import APIView

from common.mixins import EnvelopeMixin
from common.permissions import IsAdmin, IsStaffOrAdmin
from common.response import success_response

from . import services
from .models import Ticket, TicketStatus
from .serializers import TicketSerializer, TicketVerifySerializer


class TicketListView(EnvelopeMixin, generics.ListAPIView):
    """GET /api/tickets/ — 14.6절 마이페이지"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TicketSerializer

    def get_queryset(self):
        return Ticket.objects.filter(reservation_seat__reservation__member=self.request.user)


class TicketDetailView(EnvelopeMixin, generics.RetrieveAPIView):
    """GET /api/tickets/{ticket_code}/ — 14.7절"""

    def get_queryset(self):
        rows = Ticket.objects.all()
        return rows if self.request.user.is_staff or self.request.user.is_superuser else rows.filter(reservation_seat__reservation__member=self.request.user)
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TicketSerializer
    lookup_url_kwarg = "ticket_code"
    lookup_field = "ticket_code"


class StaffTicketVerifyView(APIView):
    """POST /api/staff/tickets/verify/ — 14.8절 STAFF 검표 화면, STAFF/ADMIN 공용"""

    permission_classes = [IsStaffOrAdmin]

    def post(self, request):
        serializer = TicketVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ticket = services.verify_ticket(serializer.validated_data["qr_token"], request.user)
        return success_response(TicketSerializer(ticket).data)


class AdminTicketBlockView(APIView):
    """PATCH /api/admin/tickets/{id}/block/ — 10.5절/11.1절. 18장 체크리스트 항목이
    ADMIN 전용으로 확정되어 IsAdmin으로 변경(관리자 페이지 전용 기능)."""

    permission_classes = [IsAdmin]

    def patch(self, request, ticket_id):
        ticket = Ticket.objects.get(pk=ticket_id)
        ticket.ticket_status = TicketStatus.BLOCKED
        ticket.save(update_fields=["ticket_status", "updated_at"])
        return success_response(TicketSerializer(ticket).data)

"""
참조: 14.5절(예매완료 화면 이벤트 참여 결과), 14.9절(관리자 이벤트 관리)
"""
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from common.mixins import EnvelopeMixin
from common.permissions import IsAdmin
from common.response import success_response
from reservations.models import Reservation

from . import services
from .models import Event
from .serializers import EventSerializer


class EventListView(EnvelopeMixin, generics.ListAPIView):
    """GET /api/events/"""

    queryset = Event.objects.all()
    serializer_class = EventSerializer


class EventParticipateView(APIView):
    """POST /api/events/{id}/participate/"""

    permission_classes = [IsAuthenticated]

    def post(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)
        reservation_id = request.data.get("reservation_id")
        reservation = get_object_or_404(Reservation, pk=reservation_id, member=request.user) if reservation_id else None

        if not reservation or not services.is_reservation_eligible(event, reservation):
            return success_response({"eligible": False})

        reward = services.grant_event_reward(request.user, event, reservation)
        return success_response({"eligible": True, "reward_id": reward.reward_id})


class AdminEventCreateView(EnvelopeMixin, generics.CreateAPIView):
    """POST /api/admin/events/ — 10.7절/11.1절"""

    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAdmin]

from rest_framework import serializers

from .models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["ticket_id", "reservation_seat", "ticket_code", "ticket_status", "issued_at", "used_at", "expires_at"]
        read_only_fields = fields


class TicketVerifySerializer(serializers.Serializer):
    """POST /api/tickets/verify/ 요청 바디. 7.3절: PK가 아닌 토큰으로 검증한다."""

    qr_token = serializers.CharField()

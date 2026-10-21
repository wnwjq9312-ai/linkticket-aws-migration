from rest_framework import serializers

from .models import Reservation, ReservationSeat


class ReservationCreateSerializer(serializers.Serializer):
    """POST /api/reservations/ 요청 바디"""

    schedule_id = serializers.IntegerField()
    seat_ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)


class ReservationSeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservationSeat
        fields = ["reservation_seat_id", "seat", "price"]


class ReservationDetailSerializer(serializers.ModelSerializer):
    reservation_seats = ReservationSeatSerializer(many=True, read_only=True)

    class Meta:
        model = Reservation
        fields = [
            "reservation_id", "member", "schedule", "reservation_code",
            "reservation_time", "total_amount", "reservation_status", "reservation_seats",
        ]
        read_only_fields = fields

from rest_framework import serializers

from .models import Performance, PerformanceSchedule, Seat


class PerformanceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Performance
        fields = ["performance_id", "performance_name", "venue_name", "base_price", "genre", "performance_status"]


class PerformanceDetailSerializer(serializers.ModelSerializer):
    def validate(self, data):
        latitude=data.get('latitude', getattr(self.instance,'latitude',None))
        longitude=data.get('longitude', getattr(self.instance,'longitude',None))
        if (latitude is None) != (longitude is None):
            raise serializers.ValidationError('위도와 경도를 함께 입력해주세요.')
        if latitude is not None and not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            raise serializers.ValidationError('올바른 좌표 범위를 입력해주세요.')
        if data.get('base_price',0)<0 or data.get('total_seats',1)<1:
            raise serializers.ValidationError('가격은 0 이상, 좌석 수는 1 이상이어야 합니다.')
        return data

    class Meta:
        model = Performance
        fields = "__all__"


class PerformanceScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceSchedule
        fields = [
            "schedule_id", "performance", "performance_date", "start_time", "end_time",
            "sale_status", "sale_start_at", "sale_end_at",
        ]
        # performance는 URL의 performance_id로부터 StaffPerformanceScheduleCreateView.perform_create()가
        # 채운다 — 요청 바디에서는 받지 않는다(읽기 응답에는 그대로 노출).
        read_only_fields = ["schedule_id", "performance"]


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ["seat_id", "schedule", "seat_number", "seat_grade", "seat_price", "seat_status"]

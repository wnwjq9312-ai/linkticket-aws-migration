from rest_framework import serializers

from .models import Payment


class PaymentCreateSerializer(serializers.Serializer):
    """POST /api/payments/ 요청 바디"""

    reservation_id = serializers.IntegerField()
    payment_method = serializers.CharField(max_length=20)
    coupon_id = serializers.IntegerField(required=False, allow_null=True)


class PaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"

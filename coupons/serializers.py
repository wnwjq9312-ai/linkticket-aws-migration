from rest_framework import serializers

from .models import Coupon


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ["coupon_id", "coupon_name", "discount_amount", "coupon_status", "issued_at", "expires_at"]
        read_only_fields = fields

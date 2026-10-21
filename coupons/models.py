"""
참조: 개발 기능 명세서 v2.0 3.2절(coupon)
"""
from django.db import models

from accounts.models import Member
from reservations.models import Reservation


class CouponStatus(models.TextChoices):
    AVAILABLE = "AVAILABLE", "사용 가능"
    USED = "USED", "사용 완료"
    EXPIRED = "EXPIRED", "만료"
    CANCELLED = "CANCELLED", "취소"


class Coupon(models.Model):
    coupon_id = models.AutoField(primary_key=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, db_column="member_id", related_name="coupons")
    coupon_name = models.CharField(max_length=100)
    discount_amount = models.IntegerField()
    coupon_status = models.CharField(max_length=20, choices=CouponStatus.choices, default=CouponStatus.AVAILABLE)
    issued_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    used_reservation = models.ForeignKey(
        Reservation, on_delete=models.SET_NULL, null=True, blank=True, db_column="used_reservation_id"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "coupon"

"""
참조: 개발 기능 명세서 v2.0 3.2절(payment)
"""
from django.db import models

from reservations.models import Reservation


class PaymentStatus(models.TextChoices):
    PENDING = "PENDING", "결제 대기"
    PAID = "PAID", "결제 완료"
    FAILED = "FAILED", "결제 실패"
    CANCELLED = "CANCELLED", "결제 취소"
    REFUNDED = "REFUNDED", "환불 완료"


class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    reservation = models.ForeignKey(
        Reservation, on_delete=models.PROTECT, db_column="reservation_id", related_name="payments"
    )
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_method = models.CharField(max_length=20)
    payment_amount = models.IntegerField()
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    requested_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = "payment"
        # 3.1-8절: 예매당 진행중(PENDING/PAID) 결제 1건 제약은 DB가 아닌
        # services.confirm_payment()의 애플리케이션 레벨 검증으로 강제한다.

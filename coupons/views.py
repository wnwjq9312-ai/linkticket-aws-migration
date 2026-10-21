"""
참조: 14.4절(결제 화면 쿠폰 선택), 14.6절(마이페이지)
"""
from rest_framework import generics
from rest_framework.views import APIView

from common.mixins import EnvelopeMixin
from common.response import success_response

from . import services
from .models import Coupon
from .serializers import CouponSerializer


class CouponListView(EnvelopeMixin, generics.ListAPIView):
    """GET /api/coupons/?status=AVAILABLE — 14.4절, 14.6절"""

    serializer_class = CouponSerializer

    def get_queryset(self):
        qs = Coupon.objects.filter(member=self.request.user)
        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(coupon_status=status_param)
        return qs


class CouponApplyView(APIView):
    """POST /api/coupons/{id}/apply/ — 검증만 수행, 상태 변경은 결제 성공 시점(9.2절)"""

    def post(self, request, coupon_id):
        coupon = Coupon.objects.get(pk=coupon_id)
        services.validate_coupon(coupon, request.user)
        return success_response({"coupon_id": coupon.coupon_id, "discount_amount": coupon.discount_amount})

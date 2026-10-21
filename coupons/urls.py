from django.urls import path

from . import views

urlpatterns = [
    path("coupons/", views.CouponListView.as_view(), name="coupon-list"),
    path("coupons/<int:coupon_id>/apply/", views.CouponApplyView.as_view(), name="coupon-apply"),
]

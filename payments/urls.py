from django.urls import path

from . import views

urlpatterns = [
    path("payments/", views.PaymentCreateView.as_view(), name="payment-create"),
    path("payments/<int:payment_id>/refund/", views.PaymentRefundView.as_view(), name="payment-refund"),
]

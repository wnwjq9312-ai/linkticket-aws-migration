from django.urls import path

from . import views

app_name = "payment"

urlpatterns = [
    path("", views.booking, name="booking"),
    path("checkout/", views.checkout, name="checkout"),
    path("mock-pay/", views.process_mock_payment, name="mock_pay"),
    path("complete/", views.payment_complete, name="complete"),
]

import hashlib
import json
from uuid import uuid4

from django.conf import settings
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_POST
"""
李몄“: 14.4??寃곗젣 ?붾㈃)
"""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from common.response import success_response
from coupons.models import Coupon
from reservations.models import Reservation

from . import services
from .models import Payment
from .serializers import PaymentCreateSerializer, PaymentDetailSerializer


class PaymentCreateView(APIView):
    """Create a payment for a reservation owned by the authenticated member."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        reservation = get_object_or_404(Reservation,pk=data["reservation_id"],member=request.user)
        coupon = get_object_or_404(Coupon,pk=data["coupon_id"],member=request.user) if data.get("coupon_id") else None

        payment = services.confirm_payment(reservation, data["payment_method"], coupon)
        return success_response(PaymentDetailSerializer(payment).data, status=201)


class PaymentRefundView(APIView):
    """POST /api/payments/{id}/refund/ - 결제 환불 API."""

    permission_classes = [IsAuthenticated]

    def post(self, request, payment_id):
        payment = get_object_or_404(Payment,pk=payment_id,reservation__member=request.user)
        services.refund_payment(payment)
        return success_response(PaymentDetailSerializer(payment).data)


from .forms import MockPaymentForm
from .mock_data import PERFORMANCE, DATES, PRICING, CARDS, RECOMMENDATIONS, SEATS
from .mock_services import create_mock_receipt
from .venue_data import VENUE
from .booking_context import request_booking, resolve_booking
def context():
    return {'performance': PERFORMANCE, 'dates': DATES, 'prices': PRICING, 'cards': CARDS, 'mock_config': {'seats': SEATS, 'prices': PRICING, 'fee': 2000, 'maxSeats': 4, 'dates': {d['id']: f"{d['id'][:4]}.{d['label']} {d['time']}" for d in DATES}}}

def booking(request):
    data = request_booking(request)
    from .venue_context import map_context
    data.update(map_context(data['performance']['id']))
    return render(request, 'payment/payment.html', data)

@never_cache
def checkout(request):
    data = request_booking(request)
    # Reuse the pending attempt for retry/double-click handling. A new checkout
    # after completion starts a new demo attempt.
    if not request.session.get('payment_attempt') or request.session.get('payment_receipt'):
        request.session['payment_attempt'] = uuid4().hex
    data['payment_error'] = request.session.pop('payment_error', '')
    data['payment_attempt'] = request.session['payment_attempt']
    return render(request, 'payment/checkout.html', data)

@require_POST
@never_cache
def process_mock_payment(request):
    booking_data = request_booking(request)
    form = MockPaymentForm(request.POST, booking_context=booking_data)
    if not form.is_valid():
        request.session['payment_error'] = ' '.join(str(error) for errors in form.errors.values() for error in errors)
        return redirect('payment:checkout')
    data = form.cleaned_data
    data["_booking"] = booking_data
    if data['attempt'] != request.session.get('payment_attempt'):
        request.session['payment_error'] = '결제 화면을 새로 열고 다시 시도해주세요.'
        return redirect('payment:checkout')
    fingerprint = hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    previous = request.session.get('payment_receipt')
    if previous and previous.get('attempt') == data['attempt']:
        if previous.get('fingerprint') != fingerprint:
            request.session['payment_error'] = '이미 처리된 결제 요청입니다. 결제 화면을 다시 열어주세요.'
            return redirect('payment:checkout')
    else:
        receipt = create_mock_receipt(data)
        receipt.update(attempt=data['attempt'], fingerprint=fingerprint)
        if request.user.is_authenticated:
            receipt['name'] = request.user.get_full_name() or request.user.username
            receipt['phone'] = request.user.phone_number or ''
        receipt['member_id'] = request.user.pk if request.user.is_authenticated else None
        request.session['payment_receipt'] = receipt
        history = request.session.get('payment_history', [])
        history.append(receipt)
        request.session['payment_history'] = history[-30:]
    return redirect('payment:complete')

@require_GET
@never_cache
def payment_complete(request):
    receipt = request.session.get('payment_receipt')
    if request.GET.get('receipt'):
        receipt = next((r for r in request.session.get('payment_history',[]) if r['code']==request.GET['receipt'] and r.get('member_id')==request.user.pk), None)
    if not receipt:
        return redirect('payment:checkout')
    if receipt.get('performance_snapshot'):
        data = context()
        data['performance'] = receipt['performance_snapshot']
        data['mock_config']['performanceId'] = receipt.get('performance_id', 'demo-iu')
    else:
        data = resolve_booking(receipt.get('performance_id', 'demo-iu'))
    from .venue_context import map_context
    data.update(map_context(receipt.get('performance_id','demo-iu')))
    if receipt.get('performance_snapshot',{}).get('venue_data'):
        data['venue'] = receipt['performance_snapshot']['venue_data']
        data['venue_map_config']['venue'] = data['venue']
    data['receipt'] = receipt
    data['recommendations'] = RECOMMENDATIONS
    return render(request, 'payment/payment_complete.html', data)

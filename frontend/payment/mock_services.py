"""Replace these demo boundaries with reservation/payment services, not DB schema changes."""
from uuid import uuid4
from django.utils import timezone
from .mock_data import PERFORMANCE, DATES, PRICING

METHODS = ('신용카드', '계좌이체', '가상계좌', '휴대폰 결제', '간편결제')
INSTALLMENTS = ('일시불', '2개월', '3개월', '6개월', '12개월')

def generate_reservation_code():
    # Mock identifier; replace with reservation.reservation_code on integration.
    return f"RSV-{timezone.localdate():%Y%m%d}-{uuid4().hex[:12].upper()}"

def create_mock_receipt(data):
    schedule = next(item for item in DATES if item['id'] == data['date'])
    quantity = len(data['seats'])
    subtotal = PRICING[data['grade']] * quantity
    discount = subtotal // 5 if data['discount'] == 'youth' else min(subtotal, 10000) if data['discount'] == 'coupon' else 0
    fee = quantity * 2000
    return {
        'code': generate_reservation_code(), 'title': PERFORMANCE['title'],
        'venue': PERFORMANCE['venue'], 'schedule': f"{schedule['id'][:4]}.{schedule['label']} {schedule['time']}",
        'seats': [f"1층 D구역 {s.split('-')[0]}열 {s.split('-')[1]}번" for s in data['seats']],
        'grade': data['grade'], 'quantity': quantity, 'subtotal': subtotal,
        'discount': discount, 'fee': fee, 'total': subtotal - discount + fee,
        'name': '홍길동 (테스트)', 'phone': '010-0000-0000',
        'method': data['method'], 'card': data['card'] if data['method'] == '신용카드' else '',
        'installment': data['installment'] if data['method'] == '신용카드' else '',
        'paid_at': timezone.localtime().strftime('%Y.%m.%d %H:%M:%S'),
    }

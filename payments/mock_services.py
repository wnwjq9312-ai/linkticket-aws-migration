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
    selected = data.get('_booking')
    dates = selected['dates'] if selected else DATES
    performance = selected['performance'] if selected else PERFORMANCE
    prices = selected['prices'] if selected else PRICING
    schedule = next(item for item in dates if item['id'] == data['date'])
    quantity = len(data['seats'])
    seat_data = selected.get('schedule_seats',{}).get(data['date']) if selected else None
    subtotal = sum(seat_data[s]['price'] for s in data['seats']) if seat_data is not None else prices[data['grade']] * quantity
    discount = subtotal // 5 if data['discount'] == 'youth' else min(subtotal, 10000) if data['discount'] == 'coupon' else 0
    fee = quantity * 2000
    return {
        'code': generate_reservation_code(), 'title': performance['title'], 'performance_id': performance.get('id', 'demo-iu'), 'schedule_id':schedule.get('schedule_id'), 'image':performance.get('image','payment/images/poster.webp'),
        'performance_snapshot': performance, 'venue': performance['venue'], 'schedule': f"{schedule.get('day', schedule['id'])} {schedule['time']}",
        'seats': [seat_data[s]['label'] for s in data['seats']] if seat_data is not None else [f"1층 D구역 {s.split('-')[0]}열 {s.split('-')[1]}번" for s in data['seats']],
        'grade': data['grade'], 'quantity': quantity, 'subtotal': subtotal,
        'discount': discount, 'fee': fee, 'total': subtotal - discount + fee,
        'name': '홍길동 (테스트)', 'phone': '010-0000-0000',
        'method': data['method'], 'card': data['card'] if data['method'] == '신용카드' else '',
        'installment': data['installment'] if data['method'] == '신용카드' else '',
        'paid_at': timezone.localtime().strftime('%Y.%m.%d %H:%M:%S'),
    }

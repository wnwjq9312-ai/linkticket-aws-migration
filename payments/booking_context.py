"""Resolve database schedules/seats, retaining the original demo performance map."""
from datetime import date, timedelta
from django.http import Http404
from catalog.models import Performance
from .mock_data import PERFORMANCE, DATES, PRICING, CARDS, SEATS

def resolve_booking(show_id='demo-iu'):
    if show_id.startswith('demo-'):
        from common.ui_data import SHOWS
        show = next((s for s in SHOWS if s['id'] == show_id), None)
        if not show:
            raise Http404('공연을 찾을 수 없습니다.')
        first = date.fromisoformat(show['date'])
        dates = [dict(d) for d in DATES] if show_id == 'demo-iu' else [
            dict(id=str(first+timedelta(days=i)), day=str(first+timedelta(days=i)), label=(first+timedelta(days=i)).strftime('%m.%d'), time='19:00') for i in range(3)]
        performance = dict(PERFORMANCE, title=show['title'], subtitle=show['artist'], venue=show['venue'], image=show['image'], artist=show['artist'])
        prices = dict(PRICING) if show_id == 'demo-iu' else {g: max(1000,round(show['price']*ratio/1000)*1000) for g,ratio in [('VIP',1),('R',.86),('S',.72),('A',.64)]}
    else:
        if not str(show_id).isdigit():
            raise Http404('공연을 찾을 수 없습니다.')
        try:
            p = Performance.objects.get(pk=show_id, performance_status='PUBLISHED')
        except Performance.DoesNotExist:
            raise Http404('공연을 찾을 수 없습니다.')
        dates = [dict(id=str(s.pk), day=str(s.performance_date), label=s.performance_date.strftime('%m.%d'), time=s.start_time.strftime('%H:%M'), schedule_id=s.pk) for s in p.schedules.exclude(sale_status__in=['CANCELLED','CLOSED','SOLD_OUT']).order_by('performance_date','start_time')]
        if not dates:
            raise Http404('선택 가능한 공연 회차가 없습니다.')
        performance = dict(title=p.performance_name, subtitle=p.description, venue=p.venue_name, duration='공연 안내 참고', age='공연 안내 참고', image=p.image.url if p.image else '', artist=p.performance_name)
        prices = {g:max(0,round(p.base_price*ratio/1000)*1000) for g,ratio in [('VIP',1),('R',.86),('S',.72),('A',.64)]}
    for d in dates:
        d.setdefault('day', d['id'])
    performance['id'] = show_id
    from .venue_context import venue_for
    performance['venue_data'] = venue_for(show_id)
    schedule_seats = {}
    if not show_id.startswith('demo-'):
        for d in dates:
            rows = list(p.schedules.get(pk=d['schedule_id']).seats.order_by('pk'))
            schedule_seats[d['id']] = {str(s.pk): {'grade':s.seat_grade, 'price':s.seat_price, 'label':s.seat_number, 'status':{'AVAILABLE':'available','RESERVED':'reserved','BLOCKED':'unavailable'}[s.seat_status]} for s in rows}
        registered_prices = {s['grade']:s['price'] for seats in schedule_seats.values() for s in seats.values()}
        prices = registered_prices or prices
    return {'schedule_seats':schedule_seats, 'performance':performance, 'dates':dates, 'prices':prices, 'cards':CARDS,
        'mock_config':{'performanceId':show_id, 'scheduleSeats':schedule_seats, 'seats':SEATS, 'prices':prices, 'fee':2000, 'maxSeats':4,
            'dates':{d['id']:f"{d['day']} {d['time']}" for d in dates}, 'calendar':dates}}

def request_booking(request):
    show_id = request.POST.get('performance_id') or request.GET.get('performance') or request.session.get('booking_performance','demo-iu')
    data = resolve_booking(str(show_id))
    selected = request.GET.get('schedule')
    if selected in data['mock_config']['dates']:
        data['mock_config']['initialSchedule'] = selected
    request.session['booking_performance'] = str(show_id)
    return data

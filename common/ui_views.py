from django import forms
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from accounts.serializers import RegisterSerializer
from catalog.models import Performance
from notices.models import Notice
from .ui_data import SHOWS, GENRES, DEMO_NOTICES


def catalog_rows():
    rows = list(Performance.objects.filter(performance_status='PUBLISHED').prefetch_related('schedules'))
    if not rows:
        return [dict(x) for x in SHOWS], True
    result = []
    for p in rows:
        schedule = p.schedules.order_by('performance_date').first()
        result.append(dict(id=str(p.pk), title=p.performance_name, artist=p.performance_name, genre=p.genre,
            category=p.get_genre_display(), venue=p.venue_name, region=p.address.split(' ')[0],
            date=str(schedule.performance_date) if schedule else '', price=p.base_price, image=p.image.url if p.image else '',
            dates=[str(s.performance_date) for s in p.schedules.all()], tags=[p.get_genre_display()], demo=False, description=p.description))
    return result, False


def page(request, template, data=None, **kwargs):
    data = data or {}
    data.update(kwargs)
    data.setdefault('genres', GENRES)
    return render(request, template, data)


def home(request):
    shows, demo = catalog_rows()
    return page(request, 'ui/home.html', shows=shows[:10], quick_shows=shows, demo=demo, notices=notice_rows()[:5], active='home')


def performances(request):
    shows, demo = catalog_rows()
    q = request.GET.get('q', '').strip()
    genre = request.GET.get('genre', 'all')
    region = request.GET.get('region', '')
    date = request.GET.get('date', '')
    price = request.GET.get('price', '')
    rows = [x for x in shows if (not q or q.lower() in (x['title']+x['venue']).lower()) and
            (genre == 'all' or x['genre'] == genre) and (not region or region in x['region']) and
            (not date or date in x.get('dates', [x['date']]))]
    if price in ('50000', '100000', '150000'):
        rows = [x for x in rows if x['price'] <= int(price)]
    sort = request.GET.get('sort', 'new')
    rows.sort(key=lambda x: x['price'] if sort == 'price' else x['date'], reverse=sort == 'new')
    query = request.GET.copy()
    query.pop('page', None)
    return page(request, 'ui/performances.html', shows=Paginator(rows, 12).get_page(request.GET.get('page')),
        count=len(rows), demo=demo, q=q, genre=genre, region=region, date=date, price=price, sort=sort,
        query=query.urlencode(), active='performances')


def detail(request, show_id):
    if show_id.startswith('demo-'):
        show = next((dict(s) for s in SHOWS if s['id'] == show_id), None)
        if not show:
            raise Http404
        schedules = []
    else:
        p = get_object_or_404(Performance, pk=show_id, performance_status='PUBLISHED')
        show = dict(id=str(p.pk), title=p.performance_name, category=p.get_genre_display(), venue=p.venue_name,
            description=p.description, price=p.base_price, image=p.image.url if p.image else '', demo=False)
        schedules = p.schedules.order_by('performance_date')
    from payments.booking_context import resolve_booking
    try:
        booking_dates = resolve_booking(show_id)['dates']
    except Http404:
        booking_dates = []
    from payments.venue_context import map_context
    return page(request, 'ui/detail.html', **map_context(show_id), show=show, schedules=schedules, booking_dates=booking_dates, active='performances')


@ensure_csrf_cookie
def signin(request):
    error = ''
    target = request.GET.get('next') or request.POST.get('next') or reverse('ui:home')
    if not url_has_allowed_host_and_scheme(target, {request.get_host()}, require_https=request.is_secure()):
        target = reverse('ui:home')
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user:
            login(request, user)
            return redirect(target)
        error = '아이디 또는 비밀번호를 확인해주세요.'
    return page(request, 'ui/auth.html', stage='login', error=error, next=target)


def signup(request):
    stage = 'terms'
    errors = {}
    if request.method == 'POST':
        if request.POST.get('stage') == 'terms':
            if all(request.POST.get(x) for x in ('terms', 'privacy', 'age')):
                request.session['signup_terms'] = True
                request.session['signup_marketing'] = bool(request.POST.get('marketing'))
                stage = 'information'
            else:
                errors = {'약관': ['필수 약관에 모두 동의해주세요.']}
        elif request.session.get('signup_terms'):
            stage = 'information'
            values = request.POST.dict()
            values['marketing_agree'] = bool(request.POST.get('marketing_agree'))
            serializer = RegisterSerializer(data=values)
            if request.POST.get('password') != request.POST.get('password_confirm'):
                errors = {'비밀번호': ['비밀번호 확인이 일치하지 않습니다.']}
            elif serializer.is_valid():
                serializer.save()
                request.session.pop('signup_terms', None)
                request.session['signup_complete'] = True
                return redirect('ui:register-complete')
            else:
                errors = serializer.errors
    return page(request, 'ui/auth.html', stage=stage, errors=errors, values=request.POST)


def signup_complete(request):
    if not request.session.get('signup_complete'):
        return redirect('ui:register')
    return page(request, 'ui/auth.html', stage='complete')


@require_POST
def signout(request):
    logout(request)
    return redirect('ui:home')


def notice_rows():
    rows = Notice.objects.filter(is_published=True).select_related('author').order_by('-published_at','-pk')
    return [dict(id=n.pk, title=n.title, content=n.content, category=n.get_notice_type_display(),
        author=n.author.get_full_name() or 'LINKTICKET 운영팀', image=n.image.url if n.image else '', date=(n.published_at or n.created_at).strftime('%Y.%m.%d'), views=n.view_count) for n in rows]


def notices(request):
    q = request.GET.get('q', '')
    category = request.GET.get('category', '')
    rows = [n for n in notice_rows() if q in n['title']+n['content'] and (not category or n['category'] == category)]
    return page(request, 'ui/notices.html', notices=Paginator(rows, 10).get_page(request.GET.get('page')),
        count=len(rows), q=q, active='notices', category=category)


def notice_detail(request, notice_id):
    if not str(notice_id).isdigit():
        raise Http404
    row = get_object_or_404(Notice.objects.select_related('author'),pk=notice_id,is_published=True)
    from django.db.models import F
    Notice.objects.filter(pk=row.pk).update(view_count=F('view_count')+1)
    row.refresh_from_db()
    return page(request, 'ui/notice_detail.html', notice=row, active='notices')


def help_page(request, section):
    titles = {'faq': '자주 묻는 질문', 'contact': '고객센터', 'booking': '예매 가이드', 'payment': '결제 가이드',
              'refund': '취소 / 환불 안내', 'terms': '이용약관', 'privacy': '개인정보처리방침', 'password': '비밀번호 찾기'}
    if section not in titles:
        raise Http404
    return page(request, 'ui/help.html', title=titles[section], section=section, active='notices')


@login_required
def mypage(request, section='profile'):
    from reservations.models import Reservation
    from tickets.models import Ticket
    from coupons.models import Coupon
    from events.models import DigitalCollectible, NftItem, EventReward
    valid = {'profile','reservations','tickets','coupons','interests','nft','rewards','password','notifications'}
    if section == 'membership':
        return redirect('ui:mypage')
    if section not in valid:
        raise Http404
    from .ui_forms import ProfileForm
    profile_form = ProfileForm(request.POST or None, instance=request.user) if section == 'profile' else None
    form = PasswordChangeForm(request.user, request.POST or None) if section == 'password' else None
    if request.method == 'POST':
        if section == 'profile' and profile_form.is_valid():
            profile_form.save()
            messages.success(request, '회원 정보를 저장했습니다.')
            return redirect('ui:mypage')
        if section == 'password' and form.is_valid():
            update_session_auth_hash(request, form.save())
            messages.success(request, '비밀번호를 변경했습니다.')
            return redirect('ui:mypage')
        if section == 'notifications':
            messages.info(request, '추가 회원정보 및 알림 설정 저장은 준비 중입니다.')
    # Profile/login must not eagerly query unrelated NFT or booking tables.
    collectibles = []
    nft_links_enabled = getattr(settings, 'COLLECTIBLE_LINKS_ENABLED', True)
    if section == 'nft':
        from events.ui_views import present
        nft_links_enabled = True
        collectibles = list(NftItem.objects.filter(member=request.user).select_related('performance'))
        for item in collectibles:
            present(item, request.user, request)
    elif section == 'reservations' and nft_links_enabled:
        from events.ui_views import present
        collectibles = list(DigitalCollectible.objects.filter(member=request.user).select_related('performance','source_reservation'))
        for item in collectibles:
            present(item, request.user)
    reservation_rows = list(Reservation.objects.filter(member=request.user).select_related('schedule__performance').prefetch_related('reservation_seats__ticket')) if section == 'reservations' else []
    if request.GET.get('reservation','').isdigit():
        reservation_rows = [row for row in reservation_rows if row.pk == int(request.GET['reservation'])]
    for row in reservation_rows:
        row.linked_collectibles = [item for item in collectibles if item.source_reservation_id == row.pk]
        row.owned_tickets = Ticket.objects.filter(reservation_seat__reservation=row)
    return page(request, 'ui/mypage.html', section=section, form=form, profile_form=profile_form,
        history=Paginator([r for r in reversed(request.session.get('payment_history',[])) if r.get('member_id') == request.user.pk],10).get_page(request.GET.get('mock_page')),
        reservations=Paginator(sorted(reservation_rows,key=lambda r:r.pk,reverse=True),10).get_page(request.GET.get('page')),
        tickets=Paginator(Ticket.objects.filter(reservation_seat__reservation__member=request.user).select_related('reservation_seat__reservation__schedule__performance','reservation_seat__seat').order_by('-pk') if section == 'tickets' else [],10).get_page(request.GET.get('page')),
        coupons=Paginator(Coupon.objects.filter(member=request.user).only('coupon_name','discount_amount','coupon_status','expires_at').order_by('-pk') if section == 'coupons' else [],10).get_page(request.GET.get('page')),
        collectibles=Paginator(sorted(collectibles,key=lambda x:x.pk,reverse=True),12).get_page(request.GET.get('page')),
        rewards=EventReward.objects.filter(member=request.user).select_related('event').order_by('-pk') if section == 'rewards' else [],
        receipt=request.session.get('payment_receipt'), shows=catalog_rows()[0] if section == 'interests' else [], nft_links_enabled=nft_links_enabled)


@ensure_csrf_cookie
def collected(request, page):
    return render(request, f'collected/{page}.html', {'active': 'events' if page.startswith('event') else 'nft'})


@ensure_csrf_cookie
@login_required
def operations(request, page):
    allowed = ('ADMIN',) if page == 'admin' else ('ADMIN', 'STAFF')
    if not request.user.is_active or request.user.role not in allowed:
        raise PermissionDenied('접근 권한이 없습니다.')
    return render(request, f'operations/{page}.html', {'active': page})


def venue_data(request, show_id):
    from django.http import JsonResponse
    from payments.venue_context import venue_for
    if str(show_id).isdigit():
        rows=Performance.objects.all()
        if not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)):
            rows=rows.filter(performance_status='PUBLISHED')
        get_object_or_404(rows,pk=show_id)
    elif not any(s['id']==show_id for s in SHOWS):
        raise Http404
    return JsonResponse(venue_for(show_id))

@login_required
def event_manage(request):
    from django.core.exceptions import PermissionDenied
    from events.models import Event
    from .ui_forms import EventForm
    if not request.user.is_superuser: raise PermissionDenied
    instance=get_object_or_404(Event,pk=request.GET['edit']) if request.GET.get('edit','').isdigit() else None
    form=EventForm(request.POST or None,request.FILES or None,instance=instance)
    if request.method=='POST' and form.is_valid():
        form.save();messages.success(request,'이벤트를 저장했습니다.')
        return redirect('ui:event-manage')
    return render(request,'operations/event_form.html',{'form':form,'editing':instance,'items':Paginator(Event.objects.order_by('-pk'),10).get_page(request.GET.get('page'))})


def booking_options(request, show_id):
    from django.http import JsonResponse
    from payments.booking_context import resolve_booking
    return JsonResponse({'dates':resolve_booking(show_id)['dates']})

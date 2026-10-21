from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from common.storage import nft_image_url
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import NftItem, Event
from .nft_forms import NftRegistrationForm, RewardGrantForm


def visible_collectibles(user):
    rows = NftItem.objects.select_related('performance', 'member')
    if not user.is_authenticated:
        return rows.none()
    return rows if user.is_staff else rows.filter(member=user)


def favorite_ids(request):
    return request.session.get('nft_favorites_' + str(request.user.pk), [])


def present(item, user, request=None):
    item.preview_url = nft_image_url(item.image_path)
    item.metadata_link = item.metadata_url if (item.metadata_url or '').startswith(('https://', 'http://')) else ''
    item.is_favorite = bool(request and item.pk in favorite_ids(request))
    return item


@login_required
def nft_list(request):
    rows = visible_collectibles(request.user).order_by('-issued_at')
    tab = request.GET.get('tab', 'all')
    if tab == 'owned': rows = rows.filter(member=request.user)
    if tab == 'favorites': rows = rows.filter(pk__in=favorite_ids(request))
    q = request.GET.get('q', '').strip()
    if q: rows = rows.filter(Q(nft_name__icontains=q) | Q(performance__performance_name__icontains=q))
    items = Paginator(rows, 12).get_page(request.GET.get('page'))
    for item in items: present(item, request.user, request)
    return render(request, 'ui/nfts.html', {'items': items, 'tab': tab, 'q': q, 'active': 'nft'})


@login_required
def nft_detail(request, collectible_id):
    item = present(get_object_or_404(visible_collectibles(request.user), pk=collectible_id), request.user, request)
    return render(request, 'ui/nft_detail.html', {'item': item, 'related_tickets': [], 'active': 'nft'})


@login_required
@require_POST
def nft_favorite(request, collectible_id):
    item = get_object_or_404(visible_collectibles(request.user), pk=collectible_id)
    values = set(favorite_ids(request))
    if request.POST.get('favorite') == '1': values.add(item.pk)
    else: values.discard(item.pk)
    request.session['nft_favorites_' + str(request.user.pk)] = sorted(values)
    return redirect('ui:nft') if request.POST.get('origin') == 'list' else redirect('ui:nft-detail', collectible_id=item.pk)


@user_passes_test(lambda u: u.is_authenticated and u.is_staff)
def nft_manage(request):
    form = NftRegistrationForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        item = form.save()
        messages.success(request, 'NFT를 선택한 회원에게 등록했습니다.')
        return redirect('ui:nft-detail', collectible_id=item.pk)
    return render(request, 'operations/nft_form.html', {'form': form, 'items': Paginator(NftItem.objects.select_related('member', 'performance').order_by('-issued_at'), 10).get_page(request.GET.get('page'))})


@user_passes_test(lambda u: u.is_authenticated and u.is_staff)
def reward_manage(request):
    from .services import record_event_reward
    form = RewardGrantForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        _, created = record_event_reward(**form.cleaned_data)
        messages.success(request, '보상 지급 기록을 저장했습니다.' if created else '이미 지급된 보상입니다. 기존 기록을 유지했습니다.')
        return redirect('ui:reward-manage')
    return render(request, 'operations/reward_form.html', {'form': form})

DEMO_EVENTS = [
    dict(id='demo-1',title='EARLY BIRD 할인 이벤트',category='예매 이벤트',content='예시 공연의 사전 예매 할인 안내입니다. 대상 공연과 할인 조건을 확인하세요.',image='payment/images/booking-banner.webp'),
    dict(id='demo-3',title='공연 인증샷 이벤트',category='SNS 이벤트',content='공연의 기억을 사진으로 남겨보세요. 다른 관객의 초상권을 지키고 촬영이 허용된 장소에서 참여해주세요.',image='linkticket/images/account-1.jpeg'),
    dict(id='demo-4',title='친구와 함께하는 공연',category='프로모션',content='친구와 함께 관람할 공연을 찾아보세요. 실제 할인 및 참여 접수는 운영 공지 이후 제공됩니다.',image=''),
    dict(id='demo-5',title='아티스트 사인회 초대',category='팬 이벤트',content='선정된 관객을 위한 사인회 예시 안내입니다. 신청 일정과 대상 공연은 추후 공지됩니다.',image=''),
    dict(id='demo-6',title='제휴사 할인 혜택',category='제휴 이벤트',content='제휴 혜택 예시 안내입니다. 적용 가능한 공연과 결제수단을 확인해주세요.',image=''),
]

def event_rows():
    rows = list(Event.objects.select_related('performance').order_by('-event_start'))
    if rows:
        return [dict(id=str(e.pk), title=e.event_name, category=e.event_type, start=e.event_start, end=e.event_end, status=e.get_event_status_display(), content=e.content or '상세 안내가 아직 등록되지 않았습니다.', performance=e.performance, image=e.image.url if e.image else '',demo=False) for e in rows]
    return [dict(e,start='운영 일정 미정',end='',status='미리보기',demo=True) for e in DEMO_EVENTS]

def event_list(request):
    rows = event_rows()
    category=request.GET.get('category','')
    if category: rows=[e for e in rows if e['category']==category]
    return render(request,'ui/events.html',{'events':Paginator(rows,6).get_page(request.GET.get('page')),'categories':sorted({e['category'] for e in event_rows()}),'active':'events'})

def event_detail(request):
    event_id = request.GET.get('id','demo-1')
    # Preserve old demo links without confusing them with database IDs.
    rows=event_rows()
    item=next((e for e in rows if e['id']==event_id or (e['demo'] and e['id']=='demo-'+event_id)),None)
    if not item: raise Http404('이벤트를 찾을 수 없습니다.')
    return render(request,'ui/event_detail.html',{'event':item,'active':'events'})

"""One venue adapter for the existing Kakao implementation and every UI."""
from django.conf import settings
from catalog.models import Performance
from .venue_data import VENUE

def venue_for(show_id=None):
    if show_id == 'demo-iu':
        return dict(VENUE)
    name, address, latitude, longitude = '', '', None, None
    if str(show_id).isdigit():
        p = Performance.objects.filter(pk=show_id).first()
        if p:
            name, address = p.venue_name, p.address
            latitude = float(p.latitude) if p.latitude is not None else None
            longitude = float(p.longitude) if p.longitude is not None else None
    elif show_id:
        from common.ui_data import SHOWS
        show = next((s for s in SHOWS if s['id'] == show_id), {})
        name = show.get('venue', '')
    return dict(name=name, address=address, latitude=latitude, longitude=longitude,
        subtitle='', description='공연에 등록된 공연장 정보입니다.', image='', phone='', capacity='',
        search_query=' '.join([address,name]).strip(), match_names=[name] if name else [],
        match_address=address, subway=[], buses=[], parking=[], facilities=[], notices=[],
        data_status='주소 또는 좌표가 없는 경우 운영 담당자의 정보 등록이 필요합니다.')

def map_context(show_id=None):
    venue = venue_for(show_id)
    return {'venue':venue, 'venue_map_config': {'key':settings.KAKAO_MAP_JS_KEY, 'venue':venue}}

def common_map(request):
    return map_context()

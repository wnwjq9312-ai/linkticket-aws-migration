"""Presentation-only venue contract. Replace with a venue service later.
Coordinates are intentionally unset, not guessed. The Kakao Places service
resolves the named venue and exact road address after SDK loading.
Transport, phone, capacity and venue photo are supplied UI/mock references.
"""
VENUE = {
    'name': 'KSPO DOME', 'subtitle': '올림픽체조경기장',
    'description': 'K-POP의 심장이 뛰는 대한민국 대표 공연장',
    'address': '서울특별시 송파구 올림픽로 424', 'address_note': '(올림픽공원 내)',
    'phone': '02-410-1114', 'capacity': '약 15,000명',
    'image': 'payment/images/kspo-venue.webp',
    'latitude': None, 'longitude': None, # TODO: verified venue coordinates from backend
    'search_query': 'KSPO DOME 올림픽체조경기장',
    'match_names': ['KSPO돔', 'KSPO DOME', '케이스포돔', '올림픽체조경기장', '체조경기장'],
    'match_address': '올림픽로424',
    'subway': [
        {'line': '5호선', 'color': 'purple', 'station': '올림픽공원역 3번 출구', 'walk': '도보 약 10분'},
        {'line': '9호선', 'color': 'gold', 'station': '올림픽공원역 3번 출구', 'walk': '도보 약 10분'},
        {'line': '8호선', 'color': 'pink', 'station': '몽촌토성역 1번 출구', 'walk': '도보 약 15분'},
    ],
    'buses': [
        {'type': '간선버스', 'color': 'blue', 'routes': '340, 341, 360, 362, 730'},
        {'type': '지선버스', 'color': 'green', 'routes': '3216, 3217, 3319, 3412, 3413'},
        {'type': '광역버스', 'color': 'pink', 'routes': '9403, 9507, 9607, 9701'},
    ],
    'parking': ['주차장 위치·요금·운영시간은 확인 후 제공할 예정입니다.', '공연별 주차 공지를 확인해주세요.'],
    'facilities': ['주변 편의시설 목록은 확인 후 제공할 예정입니다.', '카카오맵에서 주변 시설을 검색하실 수 있습니다.'],
    'notices': ['입장 시간·반입 제한·접근성 안내는 공연별 공지를 확인해주세요.', '현재 교통·전화·수용 규모는 제공된 시안의 Mock 안내입니다. 방문 전 실제 운영 정보를 확인해주세요.'],
    'data_status': 'Mock 안내 · 실제 운영 정보는 확인 후 연결 예정',
}

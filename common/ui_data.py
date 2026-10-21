"""Explicit presentation fixtures. Existing payment assets and demo dates are reused."""
from payments.mock_data import PERFORMANCE, DATES, RECOMMENDATIONS

SHOWS = [dict(id='demo-iu', title=PERFORMANCE['title'], artist='IU', category='콘서트', genre='CONCERT',
              venue=PERFORMANCE['venue'], region='서울', date=DATES[0]['id'], price=154000,
              image='payment/images/poster.webp', tags=['아이유', '콘서트', '서울'], demo=True)]
for index, show in enumerate(RECOMMENDATIONS, 1):
    SHOWS.append(dict(id=f'demo-{index}', title=show['name']+' '+show['subtitle'], artist=show['name'],
        category='콘서트', genre='CONCERT', venue=show['venue'], region='서울' if index != 3 else '부산',
        date=show['date'].split(' ')[0].replace('.', '-'), price=120000 + index * 5000,
        image=show['image'], tags=[show['name'], '콘서트'], demo=True))
SHOWS += [dict(id='demo-musical', title='뮤지컬 위키드', artist='WICKED', category='뮤지컬', genre='MUSICAL',
              venue='블루스퀘어', region='서울', date='2026-11-20', price=180000, image='', tags=['뮤지컬', '서울'], demo=True),
          dict(id='demo-festival', title='서울 뮤직 페스티벌', artist='SEOUL MUSIC FESTIVAL', category='페스티벌', genre='FESTIVAL',
              venue='난지한강공원', region='서울', date='2026-12-01', price=90000, image='', tags=['페스티벌'], demo=True),
          dict(id='demo-fan', title='아티스트 팬미팅', artist='BE TOGETHER', category='팬미팅', genre='FANMEETING',
              venue='장소 미정', region='서울', date='2026-12-05', price=80000, image='', tags=['팬미팅'], demo=True)]
GENRES = [('all','전체','☆'), ('CONCERT','콘서트','♬'), ('MUSICAL','뮤지컬','♫'), ('FESTIVAL','페스티벌','♧'),
          ('PLAY','연극','▥'), ('CLASSICAL','클래식','♮'), ('FANMEETING','팬미팅','◇'), ('EXHIBITION_ETC','전시/기타','✧')]
DEMO_NOTICES = [dict(id=f'demo-{i}', title=title, category=category, date='2026.09.29', content=title+'\n화면 확인을 위한 예시 공지입니다. 실제 운영 안내는 추후 등록됩니다.')
    for i,(title,category) in enumerate([('개인정보처리방침 개정 안내','공지'), ('서비스 점검 안내','점검'),
        ('티켓 예매 및 본인 확인 안내','안내'), ('IU 콘서트 추가 회차 오픈 안내','공지'),
        ('신규 가입 이벤트 안내','이벤트'), ('모바일 티켓 이용 안내','안내'), ('예매 취소 및 환불 안내','안내')],1)]

# Presentation data only. Replace this boundary with a backend service later.
PERFORMANCE = {'title': 'IU 2026 CONCERT THE WINNING', 'subtitle': '지금, 가장 빛나는 아이유의 무대', 'venue': 'KSPO DOME (올림픽체조경기장)', 'duration': '120분', 'age': '만 7세 이상 관람가'}
DATES = [{'id': '2026-11-15', 'label': '11.15 (일)', 'time': '19:00'}, {'id': '2026-11-16', 'label': '11.16 (월)', 'time': '17:00'}, {'id': '2026-11-17', 'label': '11.17 (화)', 'time': '17:00'}]
PRICING = {'VIP': 154000, 'R': 132000, 'S': 110000, 'A': 99000}
CARDS = ['신한카드', '국민카드', '삼성카드', '현대카드', '롯데카드', '하나카드', '우리카드', 'NH농협카드', '비씨카드', '씨티카드', '카카오뱅크카드', '기타카드']

RECOMMENDATIONS = [
    {'name': 'SEVENTEEN', 'subtitle': 'RIGHT HERE WORLD TOUR', 'date': '2026.12.20 (일) 18:00', 'venue': '고척스카이돔', 'image': 'payment/images/recommend-1.webp'},
    {'name': 'aespa', 'subtitle': 'SYNK : PARALLEL LINE', 'date': '2026.11.29 (일) 17:00', 'venue': '인스파이어 아레나', 'image': 'payment/images/recommend-2.webp'},
    {'name': '임영웅', 'subtitle': 'IM HERO TOUR 2026', 'date': '2026.12.27 (일) 17:00', 'venue': '부산아시아드 주경기장', 'image': 'payment/images/recommend-3.webp'},
    {'name': 'NCT DREAM', 'subtitle': 'THE DREAM SHOW 3', 'date': '2026.12.14 (월) 18:00', 'venue': '서울월드컵경기장', 'image': 'payment/images/recommend-4.webp'},
]

# Single source for the existing 10 x 16 D-section mock seating plan.
# Rows 1/9/10 remain unavailable; three reserved seats remain reserved.
def _seat_grade(row, col):
    if row <= 3 and 5 <= col <= 12:
        return 'VIP'
    if row <= 5 and 3 <= col <= 14:
        return 'R'
    if row <= 7 and 2 <= col <= 15:
        return 'S'
    return 'A'

SEATS = {
    f'{row}-{col}': {
        'grade': _seat_grade(row, col),
        'status': 'reserved' if row == 7 and 9 <= col <= 11 else 'available' if 2 <= row <= 8 else 'unavailable',
        'label': f'1층 D구역 {row}열 {col}번',
    }
    for row in range(1, 11) for col in range(1, 17)
}

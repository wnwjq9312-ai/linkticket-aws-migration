# LINKTICKET 2차 UI 개선 및 기능 보완 결과

기준 브랜치: `frontend-integration` · 기준 원격 커밋: `86f490b77d1ee3e39bf2674d59b67b35a63b0147`

검증일: 2026-09-29. 기존 1차 구현에서 이어서 수정했습니다. main 병합은 하지 않습니다. 첨부 19개 화면은 색상·카드·간격·상태 표현의 기준으로 사용했으며 기존 레이아웃과 좌석도를 우선 보존했습니다.

## 요청 항목별 결과

| 번호 | 요청 | 결과 |
|---|---|---|
| 1 | 수정 완료 화면 | 공연 상세·예매·캘린더·결제·완료·마이페이지·NFT·이벤트·공지·로그인·관리 화면 |
| 2 | UI 개선 화면 | 공통 카드/입력/버튼/표/배지, NFT 목록·상세·등록, 공지 상세, 이벤트 상세, 운영 폼 |
| 3 | 신규 기능 | DB 기반 NFT 목록·상세, 계정별 찜, NFT 이미지 업로드 등록, 공지 상세 조회·수정 API/UI, 커스텀 캘린더 |
| 4 | 기능 오류 | 고정 IU 예매, 공유 세션 저장 키, 최신 영수증만 보이던 예매내역, NFT 예매 관계 미표시, 가짜 공지 fallback 제거 |
| 5 | 공연별 예매 | IU·SEVENTEEN·aespa·DB 공연 4개를 선택해 상세 → 회차 → 좌석 → 결제 → 완료의 제목/회차/금액 유지 검증 |
| 6 | 좌석도 보존 | 원본 SEATS 160개·구역·번호·판매/선택 상태·등급·선택 로직 유지. 새 원형 좌석도로 교체하지 않음 |
| 7 | Calendar | 월 이동, 연/월, 오늘, 가능/불가 날짜, 선택 날짜와 회차, 키보드 focus, disabled 상태 구현. 외부 라이브러리 없음 |
| 8 | NFT ↔ 예매 | 기존 DigitalCollectible.source_reservation 및 Reservation → ReservationSeat → Ticket을 이용해 연결 |
| 9 | NFT 찜 | CollectibleFavorite에 회원별 저장, 재접속 유지, 명시적 찜/해제 값으로 중복 요청에도 일관된 결과 |
| 10 | 마이페이지 | 보유 티켓·보유 NFT·찜한 NFT 메뉴 분리. 예매별 티켓 상태와 연결 NFT 상세 링크 표시 |
| 11 | 이벤트 하트 | 현재 이벤트 목록 화면에서 제거 |
| 12 | 이벤트 상세 | Event ID별 DB 데이터, 데이터가 없으면 서로 다른 예시 이벤트 자료. 제목/기간/상태/내용/목록 복귀 제공 |
| 13 | 멤버십 | 사용자 메뉴·카드 제거. 기존 /mypage/membership/는 내 정보로 이동해 연결 오류 방지 |
| 14 | Social Login | Google G, Kakao TALK, Naver N, Apple 벡터 표식과 버튼 크기/간격/상태 통일. OAuth는 미구현 안내 유지 |
| 15 | 공지 UI | 유형·작성자·날짜·게시 배지·검색·유형 필터·페이지·상세 본문·조회수 제공 |
| 16 | 공지 CRUD | 기존 직원 공지 등록/삭제 보존, 같은 리소스 URL에 GET/PATCH 추가. 기존 직원 화면에서 상세/수정·취소 가능 |
| 17 | 메인 공지 | 사용자 목록/상세/메인이 같은 Notice 자료를 사용. 수정·삭제도 반영. 별도 Mock 공지 사용 안 함 |
| 18 | 관리자/직원 | 기존 URL·API·권한·등록·검표·차트 구조 유지. 관련 브라우저 회귀 검사 통과 |
| 19 | NFT 등록 | STAFF/ADMIN이 소유자·공연·예매/티켓·이미지·상태·메타데이터를 등록. ISSUED 상태는 사용자 목록에 표시 |
| 20 | 추가 발견 UI 문제 | 좁은 달력 숫자 잘림, 긴 공연명 포스터 겹침, 과하게 늘어난 좌석 카드, Reservation/Ticket object 선택지, 티켓 중복 출력 |
| 21 | 추가 개선 | 날짜 버튼 padding, 포스터 placeholder·제목 줄 수, 좌석 카드 높이, 선택지 실제 예매/티켓 번호, 업로드 버튼과 관리 상태 배지 개선 |
| 22 | 추가/수정 파일 | 문서 마지막 파일 목록 참조 |
| 23 | Model 변경 | 기존 필드 변경 없음. events에 CollectibleFavorite 모델만 추가 |
| 24 | Migration | events/0002_collectiblefavorite_and_more.py 1개 추가. 기존 migration 수정 없음 |
| 25 | 변경 이유 | 기존 구조에 회원별 NFT 찜 관계가 없으므로 회원/NFT FK와 중복 방지 unique 제약을 추가 |
| 26 | Mock 유지 | 좌석 배치·결제 승인·할인·수수료·영수증·NFT 구형 구매 체험. 실제 PG·좌석 확보·블록체인 발급 없음 |
| 27 | Django check | System check identified no issues (0 silenced) |
| 28 | 자동 테스트 | 프로젝트 루트에서 manage.py test: 전체 17개 통과 |
| 29 | URL | 공개 주요 화면 16개 HTTP 200, 로그인 상태 포함 화면 29개와 내부 링크 62개 오류 0 |
| 30 | 반응형 | 1920/1440/1280/1024/768/1920 복원 순서, 총 264회 가로 넘침 검사 통과 |
| 31 | 미연결/한계 | 아래 Mock 및 데이터 경계 참조. 실제 운영 인프라, OAuth, NFT 블록체인 발급은 범위 밖 |
| 32 | 향후 인프라 | media 저장소를 DB NFS storage로 교체하고 DB 메타데이터 유지, MariaDB migration 및 WEB 정적파일 배포 설정 필요 |

## 핵심 동작과 데이터 경계

### 공연 예매

`payments/booking_context.py`가 선택한 공연 ID를 해석합니다. DB 공연은 기존 Performance/PerformanceSchedule을 조회하며 취소·종료·매진 회차를 제외합니다. 예시 공연은 해당 공연명·이미지·장소·날짜와 가격을 사용합니다. DB 공연 가격은 기존 base_price를 Mock 등급별 비율에 적용합니다. 실제 Seat별 판매가는 연결하지 않았습니다.

상세에서 선택한 회차를 URL로 전달하고, 예매/결제의 공연 ID를 명시하며, 브라우저 저장 키도 공연별로 구분했습니다. 서버는 ID를 검증하고 해당 공연의 회차·금액으로 영수증을 만듭니다. 클라이언트에서 보낸 공연명/금액을 신뢰하지 않습니다. 세션의 Mock 영수증은 최대 30개 보관하고 개별 영수증을 다시 열 수 있습니다.

원본 좌석 모델 자료인 `payments/mock_data.py`는 수정하지 않았습니다. 좌석 JS 변경은 공연별 저장 키와 상세에서 넘어온 초기 회차 적용뿐입니다. 실제 좌석 선택/해제/등급 변경/최대 4매/판매불가 처리 함수는 유지했습니다. 160개 좌석 생성과 세부 동작을 회귀 검증했습니다.

### NFT와 예매 관계

등록된 DB 예매/티켓과 NFT의 관계는 기존 FK를 이용합니다. 등록 폼에서 연결 예매의 공연·소유자와 선택한 공연·소유자가 다르면 거부합니다. 티켓을 선택한 경우 그 티켓의 예매를 사용하며 서로 다른 예매/티켓 조합도 거부합니다. 소유자만 NFT 상세에서 연결 예매번호를 볼 수 있습니다. 타인에게는 소유자 개인정보나 예매번호를 표시하지 않습니다.

공개 NFT 목록은 ISSUED를 표시하고, 본인은 자신의 대기/실패 등 상태도 확인할 수 있습니다. 기존에 저장된 NFT를 가짜 목록 데이터로 대체하지 않습니다. 데이터가 없을 때는 빈 상태를 표시합니다. 보유 NFT와 찜은 DB에 저장됩니다.

**Mock 결제 영수증은 여전히 세션 자료이며 실제 Reservation/Payment/Ticket/NFT를 생성하지 않습니다.** 따라서 Mock 결제만으로 NFT가 자동 발급되지 않습니다. 이번 연결 검증은 기존 DB Reservation/Ticket에 관리자가 등록한 DigitalCollectible을 연결해서 수행했습니다. 기존 NFT Mock 구매 URL도 유지하고 가이드에서 체험 링크를 제공합니다. 이 구형 체험은 실제 NFT 소유권에 반영되지 않는다고 안내합니다.

### 이미지 저장

이미지는 `MEDIA_ROOT/nft/` 아래 임의 파일명으로 저장하고 기존 `DigitalCollectible.image_path`에 상대 경로를 기록합니다. Pillow로 파일 내용을 검증하며 PNG/JPEG/WebP, 최대 5MB만 허용합니다. 가짜 PNG와 소유자 불일치를 테스트했습니다. `media/`는 Git에서 제외했습니다. SVG/외부 임의 이미지를 업로드 자료로 사용하지 않습니다.

### 이벤트·공지

기존 Event 모델에는 전용 상세 본문·이미지 필드가 없습니다. DB 이벤트는 이름·기간·상태·유형을 사용하고, 본문은 연결 공연의 description 범위에서 표시하며 없는 이미지는 placeholder로 안내합니다. 전용 편집 모델을 억지로 추가하지 않았습니다. DB 이벤트가 없을 때만 각기 다른 설명을 가진 예시 이벤트가 표시됩니다. 이벤트 참여 접수/보상 발급을 새로 연결하지는 않았습니다.

Notice의 작성자·날짜·유형·게시 상태·본문·조회수를 사용합니다. 상세 조회수는 DB F 표현식으로 증가시킵니다. 기존 모델에 별도 '중요 공지' 필드가 없어 중요 여부를 임의로 만들지 않았고, 메인은 최신 공지를 표시합니다. 공지가 없으면 빈 상태를 표시합니다.

## 화면 URL

| 화면 | 경로 |
|---|---|
| 홈 / 공연 | `/`, `/performances/`, `/performance/<ID>/` |
| 선택 공연 예매 | `/booking/?performance=<ID>&schedule=<회차ID>` |
| 결제 / 완료 | `/booking/checkout/?performance=<ID>`, `/booking/complete/` |
| 개별 Mock 영수증 | `/booking/complete/?receipt=<예매코드>` |
| NFT 목록 / 내 소유 / 찜 | `/nft/`, `/nft/?tab=owned`, `/nft/?tab=favorites` |
| NFT 상세 / 찜 POST | `/nft/<ID>/`, `/nft/<ID>/favorite/` |
| 관리자·직원 NFT 등록 | `/staff/nft/` |
| 마이페이지 | `/mypage/`, `/mypage/reservations/`, `/mypage/tickets/`, `/mypage/nft/` |
| 이벤트 | `/events/`, `/events/detail/?id=<ID>` |
| 공지 | `/notices/`, `/notices/<ID>/` |
| 관리 화면 | `/dashboard/`, `/staff/`, `/staff/#notices` |
| 기존 공지 리소스 | `/api/staff/notices/<ID>/` GET/PATCH/DELETE |

예시 공연 ID: `demo-iu`, `demo-1`(SEVENTEEN), `demo-2`(aespa). DB 공연은 실제 숫자 ID를 사용합니다. 이벤트의 예시 ID는 `demo-1`, `demo-3`, `demo-4`, `demo-5`, `demo-6`입니다. NFT ID는 DB에 등록한 실제 ID이며 예시 ID를 하드코딩하지 않습니다.

## 검증 상세

- Django 전체 자동 테스트: 17개 통과. 기존 9개에 2차 기능 테스트 8개 추가.
- 모델 상태 검사: `makemigrations --check --dry-run` → No changes detected.
- Migration 적용: events.0002... OK. 기존 테이블/필드를 삭제하지 않음.
- collectstatic: 총 189개 정적 파일 정상 수집(최종 실행 5개 복사, 184개 기존).
- 공개 화면 16개: HTTP 200, 깨진 img 0개, 중복 헤더 0개, JS 예외 0개.
- 전체 이동 점검: 인증 화면을 포함한 29개 화면과 내부 링크 62개에서 4xx/5xx 0개.
- 2차 핵심 흐름: 11개 기능 검사, 17개 화면 상태 × 6개 너비 = 102회.
- 기존 가입/로그인/카드 Mock/지도/완료/티켓 모달: 49개 검사 중 48회 너비 검사.
- 일반 공개 화면: 16개 × 6개 너비 = 96회.
- 기존 운영 기능: 24개 검사 중 18회 너비 검사.
- 합계 너비 검사: 102 + 48 + 96 + 18 = **264회**, 가로 넘침 0.

Windows Microsoft Edge headless의 격리된 프로필과 합성 테스트 데이터로 검사했습니다. 각 그룹에서 1920 → 1440 → 1280 → 1024 → 768 → 1920으로 복원했습니다. OS 최대화 버튼 자체가 아닌 viewport resize 검증입니다. 주요 캡처를 육안 검토했고, 달력 날짜 버튼의 텍스트 잘림도 별도로 검사했습니다. 모든 브라우저/실기기나 모든 픽셀의 자동 비교를 의미하지 않습니다.

## 실행 / 업데이트

기존 실행 중 서버를 종료하고 새 버전으로 다시 실행하세요. Pillow 설치와 새 migration 적용이 필요합니다.

```powershell
# 저장소 루트, frontend-integration 브랜치에서
.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:DB_ENGINE = 'sqlite'
.venv\Scripts\python.exe manage.py migrate
.venv\Scripts\python.exe manage.py check
.venv\Scripts\python.exe manage.py test
.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

현재 작업 PC의 가상환경은 저장소 바로 위의 `..\venv\Scripts\python.exe`입니다. 일반 ZIP/clone 사용자는 `.venv`를 생성해서 위 명령을 사용하면 됩니다. DB_ENGINE을 설정하지 않으면 기존 MariaDB 기본 접속 설정을 사용합니다. 이번 검사에서는 MariaDB 실서버에 접속하지 않았습니다.

관리 화면은 `createsuperuser`로 만든 개발용 계정 또는 기존 STAFF/ADMIN 계정을 사용합니다. `/staff/nft/`에서 소유자와 연결 공연/예매를 선택하고 발급 완료 상태로 등록하면 사용자 NFT 목록에 표시됩니다. 테스트 비밀번호·DB·업로드 파일은 배포 ZIP/커밋에 포함하지 않습니다.

## 보존 및 향후 작업

- main, frontend 원본, 기존 migration, catalog/reservations/payments/tickets의 실거래 Service는 변경하지 않았습니다.
- 기존 Mock 결제의 receipt 생성 경계는 공연별 정보를 받도록 최소 확장했습니다.
- 사용자 지정 원형 좌석도는 적용하지 않았습니다.
- 기존 Django templates/static 표준 유지. 업로드 media만 개발환경 로컬 저장소 사용.
- DB NFS 전환 시 Django storage backend/마운트 위치를 변경하고 저장된 상대 이미지 경로를 유지하면 됩니다. MariaDB에는 NFT 메타데이터와 소유/관계/이미지 경로가 남습니다.
- WEB 정적파일은 collectstatic 산출물, 업로드는 MEDIA_URL 경로로 별도 제공해야 합니다. 권한/백업/파일 정책·운영 HTTPS 설정은 배포 단계에서 결정합니다.
- 실제 PG, MariaDB 실서버, MaxScale, WEB/DB NFS, Nginx, 물리 WEB/WAS 분리, OAuth, 실제 NFT 발급은 수행하지 않았습니다.
- 공급되지 않은 고해상도 포스터/이벤트 이미지·공식 로고 원본은 기존 자산 또는 코드 표식/placeholder로 표시합니다. 픽셀 단위 동일성은 보장하지 않습니다.

## 변경 파일 목록

수정 32개, 추가 16개.

### 수정

- `.gitignore`
- `common/test_integration.py`
- `common/ui_urls.py`
- `common/ui_views.py`
- `config/settings.py`
- `config/urls.py`
- `events/models.py`
- `notices/views.py`
- `payments/forms.py`
- `payments/mock_services.py`
- `payments/static/payment/js/payment.js`
- `payments/templates/payment/base.html`
- `payments/templates/payment/checkout.html`
- `payments/templates/payment/includes/poster.html`
- `payments/templates/payment/includes/summary.html`
- `payments/templates/payment/includes/venue_modal.html`
- `payments/templates/payment/payment.html`
- `payments/views.py`
- `requirements.txt`
- `static/linkticket/site.js`
- `static/linkticket/staff.js`
- `templates/base.html`
- `templates/collected/event_list.html`
- `templates/collected/nft_guide.html`
- `templates/collected/nft_list.html`
- `templates/operations/admin.html`
- `templates/operations/staff.html`
- `templates/ui/auth.html`
- `templates/ui/detail.html`
- `templates/ui/home.html`
- `templates/ui/mypage.html`
- `templates/ui/notices.html`

### 추가

- `common/test_phase2.py`
- `docs/FRONTEND_PHASE2.md`
- `events/forms.py`
- `events/migrations/0002_collectiblefavorite_and_more.py`
- `events/ui_views.py`
- `payments/booking_context.py`
- `static/linkticket/calendar.js`
- `static/linkticket/final-ui.css`
- `templates/includes/nft_card.html`
- `templates/includes/nft_favorite.html`
- `templates/operations/nft_form.html`
- `templates/ui/event_detail.html`
- `templates/ui/events.html`
- `templates/ui/nft_detail.html`
- `templates/ui/nfts.html`
- `templates/ui/notice_detail.html`

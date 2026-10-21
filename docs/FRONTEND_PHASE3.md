# LINKTICKET UI3 통합 결과

2026-09-30 · Repository `chltjsdnd/w` · 작업 브랜치 `frontend-integration`

기준 main: `6e6f24787a214a38dd0432516c6080b1f40495d8`. 기존 2차 통합 `8f5580a`를 이어서 수정했다. main에 merge하지 않는다. 분석 및 19개 시안 매핑은 `FRONTEND_PHASE3_ANALYSIS.md`에 기록했다.

## 1. Frontend 수정사항

- 기존 `templates/base.html`의 Header/Footer를 유지하며 UI3의 Blue → Purple → Pink, 카드·폼·버튼·배너·사이드바·페이지 번호를 공통 적용했다.
- 홈은 데스크톱 5열 인기 공연, 우측 빠른 예매/회원/공지, 하단 전체 폭 프로모션으로 구성한다. 공연 목록은 데스크톱 6열, NFT는 5열, 화면 폭에 따라 열 수가 줄어든다. 데이터가 적으면 있는 만큼 표시한다.
- `templates/ui/`의 공연, 이벤트, NFT, 공지, 로그인/가입, 마이페이지와 `templates/operations/`의 직원·관리자·등록 폼을 연결했다.
- `payments/templates/payment/`의 좌석 선택·결제·완료 구조, 카드 입력 및 약관 검증은 보존했다. 실제 DB 좌석 번호/가격은 동일 UI의 데이터 어댑터로 표시한다.
- 공연/이벤트/공지 이미지 업로드, 사진 미리보기, 공연 수정, 회차 선택 목록을 직원 화면에 연결했다.
- Google/Kakao/Naver/Apple 공식 브랜드 자산을 로컬 static에서 제공한다. 출처는 `static/linkticket/brands/README.md`. 간편 로그인 미설정 상태를 명시한다.
- UI3에는 별도 배너 원본이 없어 `imagegen` 기본 도구로 시안을 참고한 글자 없는 장식 배경을 제작했다. `static/linkticket/images/ui3-hero.png`는 실제 공연 포스터 데이터가 아니다. 개별 공연 카드는 저장된 자체 이미지만 사용하며 없으면 placeholder를 표시한다.

## 2. Backend 수정사항과 이유

|영역|파일|변경 이유와 동작|
|---|---|---|
|UI 데이터|common/ui_views.py, ui_urls.py, ui_forms.py|전체 회차 날짜 검색, 회원 정보 수정, 목록 페이지 분할, 관리자 이벤트 등록/수정, 공연별 지도/회차 JSON|
|이미지|common/uploads.py, catalog/notices/events models·serializers|기존에 없던 개별 이미지 저장; 실제 이미지 형식과 5MB 제한 검증|
|공연|catalog/serializers.py|좌표 범위·위경도 쌍 및 음수 가격/좌석 수 검증|
|예매 UI|payments/booking_context.py, forms.py, mock_services.py, views.py|DB 회차의 좌석·판매 상태·가격 연결, 서버에서 선택 좌석 검증, 영수증 당시 공연 정보 보관|
|지도|payments/venue_context.py|기존 Kakao 설정을 공연·주소·좌표 기준으로 공통화|
|NFT|events/forms.py, ui_views.py|선택한 티켓 FK 저장, Metadata URL 검증/표시, 소유자에게만 연결 티켓·예매 노출, 목록 페이지 분할|
|회원 보호|tickets/views.py, reservations/views.py, payments/views.py|타 회원의 티켓/예매/결제/환불 접근 방지와 로그인 확인|
|QR|tickets/services.py|없는 토큰을 500 대신 404 처리, EXPIRED 상태 검증 보완|
|설정|config/settings.py|공통 템플릿 태그와 지도 context processor 등록. MariaDB 기본 설정 유지|

## 3. 신규 파일

- `static/linkticket/ui3.css`: UI3 디자인과 반응형 규칙.
- `static/linkticket/date-picker.js`: 모든 날짜 입력과 예매가 공유하는 달력 렌더러.
- `static/linkticket/schedules.js`: 빠른 예매/상세의 공연 → 날짜 → 회차 연결.
- `static/linkticket/list-pages.js`: 기존 배열형 API를 사용하는 관리자 목록의 실제 행 페이지 분할 및 이미지 미리보기.
- `templates/includes/pagination.html`, `common/templatetags/ui.py`: 필터 유지, 이전/다음, 현재 페이지, 긴 페이지 목록 생략 및 media/static URL 처리.
- `templates/operations/event_form.html`, `common/ui_forms.py`: ADMIN 전용 이벤트 관리와 회원 본인 정보 수정.
- `common/uploads.py`, `payments/venue_context.py`: 업로드 검증과 공연장 데이터 어댑터.
- `common/test_phase3.py`: 신규 연동 및 권한·업로드·페이지네이션 회귀 테스트.
- 3개 추가 migration, 공식 브랜드 이미지 4개와 출처, 시안 기반 장식 배너, 분석/결과 문서.

## 4. 기존 Backend 보존과 변경 경계

`frontend/` 원본을 수정하지 않았다. 기존 URL 이름·앱·서비스 시그니처·마이그레이션·데이터를 유지한다. `payments/services.py`의 DB 결제/환불 트랜잭션, `reservations/services.py`의 Redis 선점 전제, QR 해시 발급/검표 구조와 ADMIN/STAFF 구분을 재작성하지 않았다.

현재 화면 결제는 기존 Mock 구조다. DB 공연·회차·좌석·가격을 읽어도 Mock 결제가 실제 Reservation/Payment/Ticket을 생성하거나 좌석을 확정하지 않는다. 예시 공연의 기존 160석 선택·최대 4매·할인/쿠폰 체험·중복 결제 방지도 유지한다. DB 회차에 좌석이 없으면 임의 좌석을 채우지 않는다.

관리자 배열형 API의 응답 계약은 그대로 두고 브라우저에서 10행 단위로 분할한다. 사용자 목록은 Django Paginator를 사용한다. API 수준의 대량 데이터 페이지 제한은 추후 성능 개선 대상으로 남는다.

## 5. DB 모델과 마이그레이션

|Migration|추가 필드|기존 데이터 영향|
|---|---|---|
|catalog/0002_performance_image_performance_latitude_and_more.py|Performance.image, latitude, longitude|이미지는 빈 값 허용, 좌표 nullable. 기존 공연 보존|
|events/0003_digitalcollectible_source_ticket_event_content_and_more.py|Event.content/image, DigitalCollectible.source_ticket|기존 이벤트 내용/이미지는 빈 값, 티켓 FK는 nullable/SET_NULL. 기존 예매 FK 유지|
|notices/0002_notice_image.py|Notice.image|선택적 대표 이미지, 기존 공지 본문 보존|

기존 migration 삭제·DB 초기화·기존 레코드 삭제는 하지 않았다. SQLite 개발 DB에 추가 migration 적용 완료. `makemigrations --check --dry-run`: 변경 누락 없음. 실제 MariaDB 연결 테스트는 수행하지 않았으며, MariaDB 설정의 기존 OPTIONS 유지 여부를 별도로 검사했다.

## 6. 공통 컴포넌트

- 기존 base/header/navigation/footer/search 재사용.
- 공통 Calendar: 월 이동, 오늘, 선택일, 공연 가능일/비활성, 입력 min/max. 날짜·시간 원본 ISO 값은 기존 Form/API로 전달한다.
- 공통 Kakao 모달: 기존 `payment/js/venue.js`와 `venue_modal.html` 재사용. 공연 상세·예매·완료·마이페이지 예매/티켓·직원 공연장 확인에 동일 모달을 사용한다. 키는 설정에서만 전달하며 JSON 공연장 endpoint에는 키를 넣지 않는다.
- 공통 이미지: 업로드 media URL과 기존 static 파일을 구분. cover 및 인물 중심 object-position 적용.
- 공통 페이지 번호: 검색/분류/tab 유지, 실제 데이터 수에 따른 자동 생성, 현재 페이지 표시.
- 1920/1440/1280/1024/768px 및 1920px 복귀: 열 수·헤더 줄바꿈·폼·좌석/지도·달력·footer 간격 대응.

## 7. 화면 및 기능 상태

|화면|URL|상태|
|---|---|---|
|홈|/|DB 공개 공연/공지, 빠른 공연·날짜·회차 선택|
|가입/로그인|/register/, /login/|기존 중복확인·약관·일반 세션 로그인 유지|
|공연|/performances/|검색·장르·지역·모든 회차 날짜·가격·정렬·이미지·페이지 이동|
|공연 상세|/performance/{id}/|공연 데이터, 일정 달력·회차, 공통 지도|
|좌석/결제|/booking/?performance={id}, /booking/checkout/|DB 좌석 조회/검증 또는 예시 160석, Mock 결제|
|결제 완료|/booking/complete/|공연/좌석/가격 영수증 snapshot, Mock 티켓·예매 이력·지도|
|이벤트|/events/, /events/detail/?id={id}|개별 DB 본문/이미지/분류/페이지 이동|
|NFT|/nft/?tab=all 또는 owned/favorites, /nft/{id}/|DB NFT, 찜 저장, 검색/페이지, Metadata, 소유자 전용 연결 예매/티켓|
|공지|/notices/, /notices/{id}/|직원 CRUD와 같은 DB, 이미지·검색·분류·조회·페이지|
|마이페이지|/mypage/, /mypage/reservations/, /tickets/|본인 정보 수정, DB 예매/티켓 및 별도 Mock 영수증|
|마이페이지 세부|/mypage/nft/, coupons/, interests/, password/, notifications/|NFT/쿠폰 페이지, 비밀번호/알림 저장. 공연 찜은 기존 브라우저 저장 방식 유지|
|관리자|/dashboard/|기존 대시보드·직원·회원·예매·티켓 관리 유지 및 목록 행 페이지 이동|
|직원|/staff/|공연 이미지 등록/수정 → 회차 → 좌석/가격 → 공개, 공지 CRUD/이미지, QR|
|NFT 관리|/staff/nft/|회원/공연/예매/티켓/이미지/Metadata 등록, 목록 페이지|
|이벤트 관리|/dashboard/events/|ADMIN 전용 등록/수정·이미지/기간·목록 페이지|
|QR 검표|/staff/#verify|실제 테스트 티켓의 첫 검표/중복/차단, 잘못된 토큰 처리 확인|

## 8. 테스트와 남은 연동

### 실행한 검증

- `python manage.py check`: 문제 0개.
- Django 테스트: **27개 통과**. 기존 17개 + 신규 10개. DB 공연 테스트의 좌석 값만 새로운 실제 DB 좌석 계약에 맞춰 보완했다.
- `makemigrations --check --dry-run`: No changes detected.
- `collectstatic --noinput`: 15 copied, 184 unmodified.
- 브라우저 주요 공개 화면 16개: HTTP 200, 이미지 오류/중복 헤더/JavaScript 오류 없음.
- 로그인 상태 내부 페이지 30개 및 링크 57개 검사: 404/500/JS 오류 없음.
- **258회 화면 폭 검사**: 공개 화면 96, 가입/결제 흐름 48, UI3 연결 흐름 96, 관리자/직원 18. 1920/1440/1280/1024/768/1920 복귀를 검사했다.
- 실제 브라우저로 이미지 업로드 → 공연/회차/좌석 등록 → 공개 → 지도/달력 → DB 좌석 Mock 결제 → 완료까지 통과.
- 두 번째 회차의 좌석과 가격이 결제 화면까지 유지됨, 관리자 2페이지가 실제 다른 행을 표시함, 공연 PATCH 수정 저장 확인.
- QR 정상/중복/차단, 공지 생성/삭제, 이벤트 등록/상세, 회원 가입/로그인, Mock 할인 금액과 영수증 연결을 확인했다.

### 점검 중 수정한 오류

- 사용자 정의 템플릿 태그 등록 누락 → settings에 명시 등록.
- 업로드 전 비어 있는 img → 파일 선택 후 생성.
- 날짜 변경 후 다른 회차의 저장 좌석이 사라지는 문제 → 저장된 회차 기준으로 좌석 검증.
- QR 미등록 토큰 500 → 404.
- 공연 정보 수정 후 과거 Mock 영수증 의존 → 당시 정보 snapshot.
- 설정 수정 검토에서 MariaDB OPTIONS에 불필요한 값이 섞인 것을 발견해 제거하고 원래 값 유지 검사.
- 작업 중 캐시된 템플릿과 최신 JS 혼용 → 새 검증 서버에서 재검사. 최종 결과 오류 없음.

### 미연동/의도적으로 유지한 경계

- OAuth 제공자 계정/Redirect URI, 이메일 비밀번호 재설정, 휴대폰 본인인증은 기존 서버 구현·운영 설정이 필요하다. 가짜 성공 동작을 만들지 않았다.
- Kakao 키가 없는 상태의 안내·공연장 데이터·모달을 검증했다. 실제 지도 타일/장소 검색은 유효한 JS 키와 허용 도메인 설정 후 확인해야 한다.
- 실제 Redis 선점 → DB 결제 → 티켓 전달 흐름, PG·MariaDB·MaxScale·NFS·Nginx 배포는 실행하지 않았다. 기존 서비스 코드는 보존했다.
- QR 원문은 기존 구조상 발급 때 반환되고 DB에는 해시만 저장된다. 이미 발급된 티켓에서 원문을 복원하거나 가짜 입장 QR을 만들지 않는다. 운영용 모바일 티켓 전달/재발급 정책은 별도 연결이 필요하다.
- 실제 블록체인 발급/거래 없음. Metadata 링크 표시만 지원한다.
- 공연장 실제 좌석 좌표/구역 도면은 현재 DB에 없다. 기존 좌석 도식 안에 등록된 좌석 목록을 표시하며 실제 건물 배치와 동일하다고 보장하지 않는다.
- 공연 찜은 기존 localStorage 기능이다. NFT 찜과 달리 다른 브라우저/기기 동기화는 제공하지 않는다.
- UI3의 모든 개별 고해상도 포스터·공연장 사진 원본은 별도 제공이 필요하다. 업로드 경로는 연결 완료했으며 없는 이미지를 다른 공연 이미지로 대체하지 않는다. 단일 대표 이미지 지원이며 여러 장 갤러리는 추가하지 않았다.

## 9. 환경변수 및 실행

기존 `DB_ENGINE`, DB 접속 환경변수, `KAKAO_MAP_JS_KEY`, Django SECRET_KEY/DEBUG/ALLOWED_HOSTS 설정 방식을 유지한다. 키/비밀번호 값은 이 문서에 기록하지 않는다. `MEDIA_ROOT` 업로드 파일은 배포 시 별도 보존해야 하며 저장소/소스 ZIP에는 포함하지 않는다. `STATIC_ROOT`는 collectstatic 결과물이다. WEB/WAS 분리를 위한 Django 표준 templates/static/media 구조를 유지한다.

새 checkout에서 PowerShell로 로컬 확인:

```powershell
git switch frontend-integration
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:DB_ENGINE = 'sqlite'
.venv\Scripts\python.exe manage.py migrate
.venv\Scripts\python.exe manage.py check
.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

브라우저: http://127.0.0.1:8000/ . 실제 공유 DB를 확인할 때는 기존 DB 환경변수와 접근 가능한 DB를 사용한다. 관리자 테스트는 본인 개발 환경의 계정으로 진행한다. 필요 시 `manage.py createsuperuser`로 개발 관리자 계정을 생성한다. 소스에 계정/비밀번호를 넣지 않았다.

### 장식 배너 제작 기록

기본 내장 imagegen 도구 사용. 입력 참조: UI3 메인 시안. 프롬프트: “Create a website hero BACKGROUND asset inspired by the concert hero at the top of this reference screenshot. Output ONLY a single high resolution panoramic concert photomontage, 3:1 landscape. No website interface, no letters, no titles, no logos, no card borders. Match reference's dark navy electric blue purple and pink concert lights with expressive Korean pop singers and vivid stage atmosphere. Keep leftmost 28 percent dark with subtle concert lights, empty for HTML headline overlay; singers grouped across center and right, integrated into a luminous arena concert scene. Preserve the mood and purple/pink/blue colors of the supplied hero. This is decorative website artwork, not a fake actual performance poster.”

결과 저장: `static/linkticket/images/ui3-hero.png`. 시안 원본과 이전 자산은 덮어쓰지 않았다.

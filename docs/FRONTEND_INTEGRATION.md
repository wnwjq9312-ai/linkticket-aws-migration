# LINKTICKET 프론트엔드 통합 결과

검증일: 2026-09-29. 저장소: https://github.com/chltjsdnd/w

기준 main: `6e6f24787a214a38dd0432516c6080b1f40495d8`. 결과 브랜치: `frontend-integration`. main 자동 병합 없음.

이번 결과는 Django 실행 구조의 프론트엔드 통합본입니다. 실제 PG·NFT 발급·운영 인프라는 연결하지 않았습니다. 첨부 시안의 배치·색상·카드 구조를 반영했으며, 원본 이미지·아이콘이 없는 부분까지 픽셀 단위로 동일한 결과는 아닙니다.

## 1. 통합 완료 화면

홈, 공연 목록·상세, 로그인, 3단계 회원가입, 좌석 선택, 결제 입력·완료, 공지 목록·상세, 이벤트 목록·상세, NFT 목록·가이드·Mock 구매·완료, 마이페이지 8개 영역, 관리자 5개 탭, 직원 3개 탭, 고객센터 안내를 공통 헤더·내비게이션·푸터로 연결했습니다.

공연/공지 목록은 등록된 공개 DB 데이터가 있으면 이를 사용합니다. 데이터가 없을 때만 예시 자료를 표시합니다. 이벤트와 NFT 공개 화면은 수집된 프론트의 데모 자료를 사용합니다. 직원·관리자 API는 기존 Django 데이터에 연결됩니다.

## 2. 각 화면 URL

아래 경로는 실행 서버 주소 뒤에 붙입니다. 기본 실행 예: `http://127.0.0.1:8000`.

| 화면 | URL | 조건 |
|---|---|---|
| 홈 | `/` | 공개 |
| 공연 목록 | `/performances/` | 검색·장르·지역·날짜·가격·정렬·페이지 |
| 공연 상세 | `/performance/demo-iu/`, `/performance/<공연ID>/` | DB 공연은 공개 상태 |
| 로그인 | `/login/` | Django 세션 |
| 회원가입 | `/register/` | 약관 → 정보 입력 POST |
| 가입 완료 | `/register/complete/` | 가입 완료 세션 필요 |
| 좌석 선택 | `/booking/` | IU 고정 Mock 예매 |
| 결제 입력 | `/booking/checkout/` | Mock |
| 결제 완료 | `/booking/complete/` | 유효 Mock 결제 세션 필요 |
| 공지 목록·상세 | `/notices/`, `/notices/demo-1/`, `/notices/<공지ID>/` | 공개 자료 |
| 이벤트 목록·상세 | `/events/`, `/events/detail/?id=1` | 데모 |
| NFT 목록·가이드 | `/nft/`, `/nft/guide/` | 데모 |
| NFT 구매·완료 | `/nft/payment/?id=1`, `/nft/complete/?id=1` | 클라이언트 Mock, 실제 결제 증명 아님 |
| 내 정보 | `/mypage/`, `/mypage/profile/` | 로그인 |
| 예매 내역 | `/mypage/reservations/` | 본인 데이터 + 세션 Mock 영수증 |
| 내 티켓/NFT | `/tickets/`, `/mypage/tickets/` | 로그인 |
| 쿠폰·관심 공연 | `/mypage/coupons/`, `/mypage/interests/` | 관심 목록은 브라우저 저장 |
| 멤버십 | `/mypage/membership/` | 운영 혜택 미연결 안내 |
| 비밀번호·알림 | `/mypage/password/`, `/mypage/notifications/` | 실제 변경 저장 |
| 관리자 | `/dashboard/` | 데이터 API는 ADMIN 전용 |
| 직원 | `/staff/`, `/staff/#notices`, `/staff/#verify` | 변경 API는 STAFF/ADMIN |
| 안내 | `/help/faq/`, `/help/contact/`, `/help/booking/`, `/help/payment/`, `/help/refund/` | 개발용 안내 |
| 약관·개인정보·비밀번호 찾기 | `/help/terms/`, `/help/privacy/`, `/help/password/` | 운영 정책/복구 전송 미연결 |

기존 `/api/login/`, `/api/register/` 웹 진입점과 기존 API 이름을 보존했습니다. 기존 계정 API의 중복 prefix(`/api/api/login/` 등)도 이번 변경에서 제거하지 않았습니다. 수집된 운영 UI에는 `/api/auth/login/`, `/api/auth/logout/`, `/api/auth/me/` 어댑터를 제공했습니다.

## 3. UI 이미지 기준으로 구현한 화면

| 첨부 이미지 | 연결 화면 | 반영 범위 |
|---|---|---|
| 메인페이지화면.png | `/` | 배너, 공연 카드, 빠른 검색, 공지·프로모션, 공통 구조 |
| 로그인페이지.png | `/login/` | 공연 배경·중앙 폼·우측 홍보 패널 |
| 회원가입_약간동의화면.png | `/register/` | 3단계 표시·약관·동의 |
| 회원가입_정보입력.png | 가입 정보 입력 | 2열 입력폼·중복확인·홍보 패널 |
| 회원가입_완료페이지.png | 가입 완료 | 완료 안내와 다음 행동 |
| 공연페이지화면.png | `/performances/` | 필터·정렬·공연 카드 그리드 |
| 공지사항페이지화면.png | `/notices/` | 안내 메뉴·검색·목록 |
| 이벤트페이지화면.png | `/events/` | 배너·카테고리·이벤트 카드 |
| 이벤트및nft화면페이지.png | `/nft/` | 필터·컬렉션·인기 컬렉션·가이드 |
| 결제페이지화면.png | `/booking/` | 좌석·등급·날짜·예매 요약 |
| 결제화면페이지.png | `/booking/checkout/` | 선택 공연·구매자·결제수단·동의·합계 |
| 관리자페이지화면.png | `/dashboard/` | 좌측 메뉴·배너·KPI·차트·표 |

시안과의 차이: 일부 포스터·이벤트 일러스트·아이콘 원본이 없어 기존 이미지 또는 준비 중 표시를 사용했습니다. 데이터에 따라 카드 수·표 행이 달라집니다. 관리자 차트는 기존 API에서 조회 가능한 좌석 통계를 사용하며, 미연결 인프라 상태를 정상 수치로 꾸미지 않았습니다. 실결제가 없는 상태임을 알리는 Mock 문구가 추가됐습니다.

## 4. 별도 UI 이미지가 없어 Design System 기준으로 구현한 화면

공연 상세, 이벤트 상세, NFT 가이드·구매·완료, 결제 완료, 마이페이지, 직원 공연·공지·QR 관리, 공지 상세 및 고객센터 안내는 동일한 남색/파랑 텍스트, 연한 배경, 흰 카드, 얇은 테두리, 보라·분홍 강조색을 적용했습니다. 폼·버튼·표·상태 안내·모달의 간격과 표시를 정리했습니다.

## 5. 추가/수정 파일 및 원본 대응

| 원본 영역 | 실행 구조 | 처리 |
|---|---|---|
| frontend/web | templates/ui + common/ui_views.py | Django 데이터·URL·공통 레이아웃 연결 |
| frontend/account | accounts + templates/ui/auth.html | 기존 모델/serializer 유지, 회원가입·로그인 화면 통합 |
| frontend/events | templates/collected + static/linkticket/collected | 본문/상호작용 이관, HTML·CSS·JS 분리 |
| frontend/payment | 기존 payments 앱 | 이미 존재하는 중복본을 활용, 공통 base와 URL 연결 |
| frontend/admin·staff·shared | templates/operations + static/linkticket | 기존 API 호출과 폼 유지, 스타일 통일·세션 어댑터 |

`frontend/` 원본은 수정하지 않았습니다. 파일별 목록은 문서 마지막에 있습니다. `templates/base.html`과 `templates/includes/`가 공통 레이아웃입니다. `static/linkticket/site.css`, `refinements.css`가 공통 스타일과 시안 보정이며, 수집된 화면 CSS는 범위를 제한해 충돌을 줄였습니다.

## 6. 기존 코드 변경 내용과 이유

- accounts/models.py: 기존 권한 코드가 참조하지만 빠져 있던 MemberRole, role, member_id를 호환 속성으로 복원했습니다. is_superuser/is_staff를 기반으로 하며 DB 필드 추가/삭제는 없습니다.
- accounts/apps.py: 기존 migration의 BigAutoField와 기본값을 맞춰 불필요한 migration 생성을 방지했습니다.
- accounts/views.py: 레거시 웹 진입점은 통합 로그인·가입 화면으로 연결하고 로그인 정보 출력문을 제거했습니다.
- config/settings.py: 전역 templates, 프로젝트 static, STATIC_ROOT, LOGIN_URL, 환경변수 지도 키를 설정했습니다. 기존 MariaDB 기본값과 SQLite opt-in 방식을 유지했습니다.
- config/urls.py: UI·Mock 결제·세션 어댑터 라우트를 추가했습니다. 기존 API 라우트를 제거하지 않았습니다.
- payments/forms.py와 views.py: 깨진 한글 오류 문구와 카드 결제수단 비교 문자열을 복구했습니다. 잘못된 카드 입력 검증 우회를 막았습니다.
- payment base/includes/완료 화면: 중복 헤더·푸터를 제거하고 홈·마이페이지·공연 탐색으로 연결했습니다.
- 기존 Service와 Migration 파일은 수정하지 않았습니다. 원본 models의 스키마를 바꾸지 않았습니다.

## 7. 반응형 수정

1920·1440·1280·1024·768px에서 컨테이너, 카드 열 수, 폼·결제 요약, 운영 메뉴·차트·표를 조정했습니다. 공통 헤더는 좁은 화면에서 내비게이션을 다음 줄로 배치합니다. NFT는 작은 화면에서 필터·목록·보조 카드를 재배치합니다. 표는 필요한 경우 카드 내부에서 스크롤합니다. 1280px 결제 페이지의 좌우 margin 문제와 NFT의 고정 폭 문제를 수정했습니다. `[hidden]`이 flex/grid 스타일에 덮이지 않게 처리했습니다.

동일 페이지에서 1920 → 1440 → 1280 → 1024 → 768 → 1920 순으로 크기를 바꿔 복원 시 가로 넘침을 확인했습니다. 이는 브라우저 viewport 변경 검사이며 OS 최대화 버튼 자체를 자동 조작한 검사는 아닙니다.

## 8. Mock 유지 기능

고정 IU 예시 공연·날짜·좌석·등급·최대 4매·할인·수수료·합계, 결제수단 선택, 필수 동의, `DEMO` 승인코드, 중복 결제 제출 방지, 세션 영수증, 모의 티켓/지도 모달을 유지했습니다. VIP 2석 + 청소년 할인 + 수수료의 합계 250,400원을 브라우저에서 검증했습니다. 실제 좌석 확보·PG 승인·DB 예매 생성·입장 가능한 QR 발급은 하지 않습니다.

NFT 구매는 클라이언트 Mock 흐름입니다. 실제 결제, 입금 계좌 생성, 이메일 전송, 블록체인 발급은 없습니다. 예시 수량·가격·인기도는 운영 통계가 아닙니다.

## 9. 미구현/미연결 기능

- DB 공연의 실시간 좌석/회차와 Mock 결제 간 연결: 현재 상세에서 IU 예시 체험임을 안내합니다.
- 실제 PG·실시간 좌석 Redis Lock·예매 확정·환불의 운영 종단간 연결 및 부하/동시성 검증.
- NFT 발급·지갑·소유권 검증, 이벤트 참여/보상 저장, NFT 구매내역 DB 기록.
- SMS 본인인증·아이디/비밀번호 복구 메일, 프로필 사진·내 정보 수정·회원탈퇴·운영 멤버십.
- 실운영 약관, 고객센터 문의 접수, 리뷰 작성, 인프라 상태 모니터링.
- 관심 공연은 브라우저 로컬 저장이며 계정 간 동기화되지 않습니다.

기존 관련 Skeleton/API/Service는 유지했습니다. 화면에 미연결 안내를 제공하는 항목을 완성된 운영 기능으로 표시하지 않았습니다.

## 10. 추가로 필요한 이미지

시안의 고해상도 메인/로그인 배경, 장르별 공연 포스터 전체, 이벤트별 배너·일러스트, NFT별 원본 썸네일, 로고 벡터·통일 아이콘 세트가 필요합니다. 현재 일부 자료는 기존 저해상도 assets를 확대하므로 흐릿합니다. 위키드/페스티벌 등 없는 포스터는 준비 중 표시입니다. 관리자 홍보 배너는 기존 회원가입 이미지에서 추출한 이미지를 재사용했습니다.

## 11. 백엔드/DB/NFS 연동 필요 부분

이번 검증은 별도 로컬 SQLite DB에서 수행했습니다. MariaDB·MaxScale·WEB NFS·DB NFS·Nginx·실제 PG 연결은 수행하지 않았습니다. 향후 Django가 HTML/API를 제공하고 WEB이 collectstatic 산출물을 제공할 수 있도록 표준 templates/static 구조를 유지했습니다. 실제 운영에서는 정적/미디어 경로, 공유 저장소, 세션·Redis, DB 접속, 운영 secret·호스트·HTTPS 정책과 도메인별 Kakao 키 허용 설정을 팀 배포 구성에 맞춰 연결해야 합니다.

`KAKAO_MAP_JS_KEY`는 환경변수에서만 읽습니다. 미설정 시 주소 안내를 표시합니다. 실제 Kakao 지도 로딩은 유효 키가 제공되지 않아 검증하지 않았습니다.

## 12. Django 검사 결과

로컬 Python 3.x / Django 4.2.30 / SQLite에서 실행:

```text
python manage.py check
System check identified no issues (0 silenced).

python manage.py makemigrations --check --dry-run
No changes detected

python manage.py test common.test_integration --verbosity 1
Found 9 test(s).
Ran 9 tests — OK

python manage.py collectstatic --noinput
187 static files copied (최초 수집)
```

테스트는 인증·CSRF·안전한 로그인 이동, 가입 단계, 마이페이지, 권한 분리, 직원 계정 발급·정지, Mock 결제 합계·중복/변조 거부, 검색·지도 키 누락, 공연·회차·좌석·공지 등록/삭제·관리자 통계를 포함합니다. 운영 DB의 동시성·성능·배포 검증 결과는 아닙니다.

## 13. 주요 URL 및 흐름 테스트 결과

Microsoft Edge headless의 분리된 테스트 프로필을 사용했습니다. 합성 계정·로컬 테스트 자료만 사용했습니다.

- 공개 주요 화면 16개: HTTP 200, 중복 헤더 없음, 깨진 img 0개, JS 예외 0개.
- 내부 링크 63개: HTTP 4xx/5xx 0개. 일부 로그인 필요 링크는 정상 리다이렉트 포함.
- 가입 → 로그인 → 마이페이지, 좌석 → Mock 카드 결제 → 완료 → 예매내역 연결: 통과.
- 이벤트/NFT 필터, NFT Mock 간편결제 → 완료, 지도 키 누락 안내: 통과.
- 직원 공연·회차·좌석 등록과 공개, 공지 등록·삭제, QR 검표·중복입장 거부: 통과.
- 관리자 실데이터 차트 100% 표시, 티켓 차단, 로그아웃: 통과.

## 14. 화면 크기별 테스트 결과

| viewport | 공개 화면 | 가입/결제 등 8개 상태 | 운영 데이터 3개 상태 |
|---|---:|---:|---:|
| 1920 | 16 통과 | 8 통과 | 3 통과 |
| 1440 | 16 통과 | 8 통과 | 3 통과 |
| 1280 | 16 통과 | 8 통과 | 3 통과 |
| 1024 | 16 통과 | 8 통과 | 3 통과 |
| 768 | 16 통과 | 8 통과 | 3 통과 |
| 1920 복원 | 16 통과 | 8 통과 | 3 통과 |

공개 화면 96회, 가입·결제 상태 48회, 운영 상태 18회 총 162회의 viewport 가로 넘침 검사 통과. 별도 기능 점검을 합하면 흐름 검사 52개, 운영 검사 24개입니다. screenshots의 핵심 화면을 육안 검토했습니다. 모든 픽셀에 대한 자동 시안 비교, Safari/Firefox/실제 모바일 장치 검증은 수행하지 않았습니다.

## 15. 발생 오류와 해결

| 오류/차이 | 해결 |
|---|---|
| MemberRole import 오류로 Django 기동 실패 | 스키마 변경 없이 권한 호환 속성 추가 |
| 계정 기본 PK와 migration 불일치 | BigAutoField 설정 일치 |
| 결제 UI 진입 URL 미연결 | payment namespace를 /booking/에 include |
| HTML 주석 내부 Django 태그 실행으로 500 | 통합본의 문제 주석 제거 |
| 깨진 한글 결제수단 문자열 | 카드 비교·오류 메시지 복원 |
| 공통/수집 CSS 충돌과 hidden 무시 | CSS 범위 제한·hidden 규칙 보정 |
| 1280 결제 가로 넘침·768 NFT 불균형 | margin/grid/min-width 규칙 수정 |
| NFT 수량 24와 실제 카드 수 불일치 | 초기 로드에도 필터 집계 실행 |
| 로그아웃 뒤 운영 데이터 잔존 | 로그아웃 후 페이지 재로드 |
| 오래된 개발 서버가 캐시된 템플릿 제공 | 최종 검사는 새 포트의 새 프로세스에서 수행 |
| 공지 삭제 테스트가 204를 기대 | 기존 envelope 응답 200에 맞춰 검사하고 DB 삭제 확인 |

## 실행 및 검토 방법

저장소를 받은 뒤 `frontend-integration`을 체크아웃합니다. main 병합은 사용자 확인 이후 별도 결정합니다.

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:DB_ENGINE = 'sqlite'
.venv\Scripts\python.exe manage.py migrate
.venv\Scripts\python.exe manage.py check
.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

운영 화면을 확인할 로컬 관리자 계정은 별도로 생성하세요. 테스트 계정·비밀번호·SQLite DB는 결과 저장소에 포함하지 않습니다.

```powershell
.venv\Scripts\python.exe manage.py createsuperuser
.venv\Scripts\python.exe manage.py test common.test_integration
```

설정 예시는 `.env.example`을 참고하세요. DB_ENGINE을 설정하지 않으면 기존 설정대로 MariaDB 연결을 시도합니다. `collectstatic`의 출력 디렉터리 `staticfiles/`는 커밋하지 않습니다.

## 파일별 변경 목록

기존 파일 수정 14개, 신규 파일 51개.

### 수정

- `.env.example`
- `.gitignore`
- `accounts/apps.py`
- `accounts/models.py`
- `accounts/views.py`
- `config/settings.py`
- `config/urls.py`
- `payments/forms.py`
- `payments/static/payment/js/payment.js`
- `payments/templates/payment/base.html`
- `payments/templates/payment/includes/footer.html`
- `payments/templates/payment/includes/header.html`
- `payments/templates/payment/payment_complete.html`
- `payments/views.py`

### 추가

- `accounts/integration_urls.py`
- `accounts/integration_views.py`
- `common/test_integration.py`
- `common/ui_data.py`
- `common/ui_urls.py`
- `common/ui_views.py`
- `docs/FRONTEND_INTEGRATION.md`
- `static/linkticket/admin.js`
- `static/linkticket/api.js`
- `static/linkticket/collected/event_detail.css`
- `static/linkticket/collected/event_detail.js`
- `static/linkticket/collected/event_list.css`
- `static/linkticket/collected/event_list.js`
- `static/linkticket/collected/nft_guide.css`
- `static/linkticket/collected/nft_guide.js`
- `static/linkticket/collected/nft_list.css`
- `static/linkticket/collected/nft_list.js`
- `static/linkticket/collected/nft_payment.css`
- `static/linkticket/collected/nft_payment.js`
- `static/linkticket/collected/nft_payment_complete.css`
- `static/linkticket/collected/nft_payment_complete.js`
- `static/linkticket/images/account-0.jpeg`
- `static/linkticket/images/account-1.jpeg`
- `static/linkticket/operations.css`
- `static/linkticket/refinements.css`
- `static/linkticket/site.css`
- `static/linkticket/site.js`
- `static/linkticket/staff.js`
- `templates/base.html`
- `templates/collected/event_detail.html`
- `templates/collected/event_list.html`
- `templates/collected/nft_guide.html`
- `templates/collected/nft_list.html`
- `templates/collected/nft_payment.html`
- `templates/collected/nft_payment_complete.html`
- `templates/includes/categories.html`
- `templates/includes/footer.html`
- `templates/includes/header.html`
- `templates/includes/help_nav.html`
- `templates/includes/hero.html`
- `templates/includes/navigation.html`
- `templates/includes/show_card.html`
- `templates/operations/admin.html`
- `templates/operations/staff.html`
- `templates/ui/auth.html`
- `templates/ui/detail.html`
- `templates/ui/help.html`
- `templates/ui/home.html`
- `templates/ui/mypage.html`
- `templates/ui/notices.html`
- `templates/ui/performances.html`

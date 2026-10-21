# LINKTICKET Django 스켈레톤

이 디렉터리는 "LINKTICKET 개발 기능 명세서 v2.0 (통합본)"(+ v2.3 수정본 반영)을 코드로
옮긴 **뼈대(skeleton)**다. 목적은 하나뿐이다:

> **모델/시리얼라이저/뷰/URL/서비스 함수의 이름을 이 저장소가 "정답"으로 고정한다.**
> 팀원 5명이 서로 다른 PC에서 서로 다른 AI 도구로 이어서 개발하더라도,
> 이 스켈레톤 위에 코드를 채워 넣는 이상 이름이 갈라질 수 없다.

명세서 문서(마크다운/Claude Docs)는 "설계 의도"를 설명하지만, AI에게 매번 새로 해석시키면
`member_id` vs `memberId` vs `user_id`, `hold_seat` vs `reserve_seat_temp` 같은 사소한
불일치가 반드시 발생한다. 이 스켈레톤은 그 해석 단계 자체를 없앤다.

## 로컬에서 화면 띄우기 (아래 명령어를 그대로 실행하면 됨)

팀 확정 DB는 **MariaDB**이고, `config/settings.py`의 기본값도 MariaDB(mysql 엔진)다 —
SQLite가 기본이 아니다. 그래서 로컬에서 띄우려면 먼저 접속할 MariaDB가 하나 필요하다.
접속 대상은 셋 중 하나면 된다: (a) DB 담당 조원의 PC(팀 공유 DB), (b) db-master
(10.10.1.2), (c) 내 컴퓨터에 직접 설치한 MariaDB(순수 화면 확인용). 접속 정보만 있으면
코드는 그대로다.

```bash
# 1) 압축 풀고 그 폴더로 이동
unzip linkticket_skeleton.zip
cd linkticket_skeleton

# 2) 가상환경 생성 + 패키지 설치
python3 -m venv .venv
source .venv/bin/activate        # Windows는 .venv\Scripts\activate
pip install -r requirements.txt

# 3) .env 생성 — MariaDB 접속 정보 입력 (.env.example 참고)
cp .env.example .env
# .env를 열어서 DB_HOST/DB_NAME/DB_USER/DB_PASSWORD를 채운다
#   예: DB를 들고 있는 조원 PC IP, 또는 내가 로컬에 새로 설치한 MariaDB면 127.0.0.1

# 4) DB 테이블 생성 (이미 만들어둔 migrations를 그대로 적용)
python manage.py migrate

# 5) 로그인할 관리자 계정 하나 생성
python manage.py shell -c "
from accounts.models import Member
Member.objects.create_superuser(login_id='admin', email='admin@example.com', password='admin1234!')
"

# 6) 서버 실행
python manage.py runserver
```

**MariaDB에 아직 붙일 수 없고 화면 UI만 잠깐 보고 싶다면**, 3번 대신 `.env`에
`DB_ENGINE=sqlite` 한 줄만 넣으면 된다 — 이건 DB 서버 없이 화면만 확인하는 예외
경로이고, 그 데이터는 팀 공유 DB와 무관한 완전히 별개의 로컬 파일이다(`db.sqlite3`).
정식 등록 검증은 반드시 위 MariaDB 경로로 다시 확인해야 한다.

서버가 뜨면 브라우저에서 아래 두 주소를 열면 된다(같은 서버가 API와 화면을 함께
서빙하므로 별도 세팅이 필요 없다):

- 직원 페이지: http://127.0.0.1:8000/static/staff/index.html
- 관리자 페이지: http://127.0.0.1:8000/static/admin/index.html

두 페이지 모두 위에서 만든 `admin` / `admin1234!`로 로그인하면 된다(role이 ADMIN이라
STAFF 전용 API까지 전부 접근 가능). 이 순서는 실제로 실행해서 로그인→공연/회차/좌석
등록→직원 계정 발급→대시보드 조회까지 끝까지 확인했다.

## 팀 사용 규칙 (필독)

1. **이 스켈레톤을 그대로 공유 저장소(Git)에 커밋한다.** 브랜치를 나누더라도 이 구조는
   건드리지 않는다.
2. **어떤 AI 도구를 쓰든, 프롬프트에 반드시 다음을 포함시킨다.**
   > "아래는 우리 팀이 이미 확정한 Django 스켈레톤이다. 새로 설계하지 말고, 이 파일들의
   > 기존 클래스/함수/필드 이름과 시그니처를 그대로 사용해서 **내부 구현부만** 채워라.
   > 이름이 명세서와 다르면 반드시 스켈레톤 쪽을 따른다."
   그리고 채우려는 파일(예: `payments/services.py`)의 **현재 내용 전체**를 함께 붙여넣는다.
3. **함수 시그니처(인자 이름, 인자 순서, 반환 타입)를 바꾸지 않는다.** 시그니처를 바꿔야 할
   필요가 생기면, 개인 판단으로 바꾸지 말고 반드시 팀에 공유 후 이 스켈레톤과
   "네이밍 컨벤션 규칙" 문서를 함께 갱신한다.
4. **새 앱/모델/필드가 필요하면** 이 README와 네이밍 컨벤션 문서에 먼저 규칙을 추가하고,
   그 규칙에 맞춰 스켈레톤에 반영한 뒤 배포한다. "일단 로컬에서 편하게 이름 짓고 나중에
   맞춘다"는 방식은 금지한다 — 그 순간 팀 간 불일치가 시작된다.
5. **각 서비스 함수 docstring의 "참조: 명세서 X.X절"을 지우지 않는다.** 구현 중 명세서와
   충돌이 발견되면 그 자리에 `# TODO(spec-conflict): ...` 주석을 남기고 팀에 알린다.
6. **`views.py`에 `rest_framework.generics`의 `ListAPIView`/`CreateAPIView`/
   `RetrieveAPIView`/`UpdateAPIView`/`ListCreateAPIView`를 새로 상속할 때는 반드시
   `common.mixins.EnvelopeMixin`을 상속 목록 맨 앞에 같이 넣는다**
   (`class FooListView(EnvelopeMixin, generics.ListAPIView):`). 안 넣으면 그 API만
   `{"success": true, "data": ...}` 표준 봉투를 안 타고 raw `serializer.data`가 그대로
   나가서, `frontend/shared/api.js`(모든 응답이 이 봉투라고 가정하고 `payload.data`를
   꺼내 쓴다)에서 그 API를 호출하는 화면 로직만 조용히 깨진다 — 최초 스켈레톤에서 이
   실수가 실제로 있었고, 이번에 21개 뷰 전체를 찾아서 고쳤다.

## 앱 구조 및 담당 테이블

| 앱 (Django app) | 담당 DB 테이블 | 핵심 책임 |
|---|---|---|
| `accounts` | `member` | 인증(Custom User Model), 회원 CRUD, 권한(CUSTOMER/STAFF/ADMIN) |
| `catalog` | `performance`, `performance_schedule`, `seat` | 공연/회차/좌석 조회, Redis 기반 좌석 임시선점 |
| `reservations` | `reservation`, `reservation_seat` | 예매 생성/취소, 좌석-예매 매핑 |
| `payments` | `payment` | 결제 확정/환불 — 전체 트랜잭션의 오케스트레이션 허브 |
| `tickets` | `ticket` | QR 토큰 발급/해시/검표 |
| `coupons` | `coupon` | 쿠폰 검증/사용/환불 시 복원 |
| `events` | `event`, `event_reward`, `digital_collectible` | 사회공헌 이벤트, 리워드, Digital Collectible 발급 |
| `notices` | `notice` | 공지/이벤트/안내/점검 공지사항 (v2.3 `notice_type` 반영) |
| `common` | (테이블 없음) | 공통 예외, 응답 포맷, 권한, Redis 클라이언트/키 규칙 |
| `dashboard` | (테이블 없음) | 관리자 페이지 모니터링 대시보드 집계(예매 인원/미판매 좌석/매출). 다른 앱의 `services.py`를 조합만 하는 유일한 read-전용 앱 |

## 앱 간 의존 방향 (순환 참조 금지)

```
accounts ─┬─▶ catalog ─▶ reservations ─┬─▶ payments ──▶ tickets
          │                            ├─▶ tickets
          │                            └─▶ coupons
          ├─▶ events (accounts만 참조)
          └─▶ notices (accounts만 참조)

dashboard ─▶ catalog / reservations / payments  (read-전용, 역방향 금지)
```

`payments/services.py`가 `catalog`, `reservations`, `tickets`, `coupons`의 서비스 함수를
호출하는 최상위 오케스트레이터다. **역방향 import(예: `tickets`가 `payments`를 import)는
금지** — 순환 참조가 발생한다. 새 의존성이 필요하면 먼저 이 다이어그램을 갱신한다.

## 로컬 실행에 필요한 건 이미 다 들어있다 / 운영 배포 전 바꿔야 하는 것

`manage.py`, `config/settings.py`(SQLite, 개발용), `config/wsgi.py`, 각 앱의 `__init__.py`
/ `apps.py` / `migrations/0001_initial.py`, `requirements.txt`까지 포함되어 있어서 위
"로컬에서 화면 띄우기" 순서만 따라 하면 바로 실행된다(위 순서로 실제로 로그인부터
대시보드 조회까지 확인 완료). 의도적으로 아직 넣지 않은 것:

- `config/asgi.py`(WebSocket 등 비동기 기능 쓰기 전까지는 불필요)
- 각 앱의 `admin.py`(Django 기본 관리자 사이트용 등록. `/admin-site/`는 현재 빈 상태),
  `tests.py`
- 운영용 `config/settings.py` — 지금 들어있는 건 SQLite 기반 **개발용**이다. 운영
  전환 시 아래 MariaDB 설정과 Ansible Vault 기반 시크릿 관리로 반드시 교체해야 한다.

### `settings.py`에 반드시 들어가야 하는 항목 (운영 배포용 — 지금의 개발용 SQLite 설정을 대체)

```python
AUTH_USER_MODEL = "accounts.Member"

INSTALLED_APPS = [
    ...,
    "rest_framework",
    "accounts",
    "catalog",
    "reservations",
    "payments",
    "tickets",
    "coupons",
    "events",
    "notices",
    "dashboard",
]

REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "common.exception_handler.linkticket_exception_handler",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        # 팀 확정 시 TokenAuthentication 또는 JWT로 교체
    ],
}

# WAS Zone(10.10.2.0/24) 내 was-redis(10.10.2.6) 참조.
# common/redis_client.py의 기본값과 반드시 일치시킬 것.
REDIS_URL = "redis://10.10.2.6:6379/0"

# DB Zone(10.10.1.0/24): db-master(10.10.1.2) / MaxScale은 WAS Zone(10.10.2.5)에서 프록시
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "HOST": "10.10.2.5",  # was-maxscale 경유, db-master 직접 접속 금지
        "PORT": 3306,
        "NAME": "linkticket",
        # USER/PASSWORD는 Ansible Vault로 관리 (평문 커밋 금지)
    }
}
```

## 파일 트리

```
common/
  error_codes.py       공통 오류코드 상수 + STATUS_CODE_MAP
  exceptions.py         LinkTicketError 및 14개 서브클래스
  response.py           success_response / error_response
  mixins.py              EnvelopeMixin — generics.*APIView 응답을 표준 봉투로 통일
  exception_handler.py  DRF EXCEPTION_HANDLER
  permissions.py        IsAdmin / IsStaffOrAdmin / IsOwner
  redis_client.py        redis-py 클라이언트 싱글턴
  redis_keys.py          Redis 키 생성 함수 + TTL/제한값 상수

accounts/{models,serializers,views,urls}.py
catalog/{models,serializers,services,views,urls}.py
reservations/{models,serializers,services,views,urls}.py
payments/{models,serializers,services,views,urls}.py
tickets/{models,serializers,services,views,urls}.py
coupons/{models,serializers,services,views,urls}.py
events/{models,serializers,services,views,urls}.py
notices/{models,serializers,views,urls}.py
dashboard/{services,views,urls}.py   # 모델 없음 — 다른 앱 services.py 조합 전용

config/urls.py   루트 URLConf (/api/ 프리픽스, /admin-site/는 Django 기본 admin)

frontend/
  shared/api.js     공통 fetch 래퍼 (세션 쿠키 + CSRF 헤더 + 표준 응답 언랩)
  shared/style.css  공통 스타일(팀 데이터 시각화 팔레트 토큰)
  staff/index.html, staff/app.js    직원 페이지
  admin/index.html, admin/app.js    관리자 페이지
```

## 직원/관리자 페이지 (`frontend/`)

Django 템플릿이 아닌 **정적 HTML + vanilla JS**로 만들었다. WEB Zone(nginx)이 이 정적
파일을 서빙하고 `/api/`로 오는 요청만 WAS Zone(Django+Gunicorn)으로 리버스 프록시한다는
기존 Zone 구조를 그대로 따른 것이다. React/Vue 등 프레임워크를 팀이 아직 확정하지
않았다면, 이 폴더가 "일단 동작하는" 기준선이고 나중에 프레임워크로 옮겨갈 때도 호출하는
API 목록(=네이밍 컨벤션 문서 12.2절)은 그대로 재사용할 수 있다.

- **직원 페이지(`frontend/staff/`)**: 공연 올리기(공연 등록 → 회차 등록 → 좌석 일괄 등록
  3단계), 공지 올리기/삭제, QR 검표. `IsStaffOrAdmin` 권한이 걸린 `/api/staff/*` API만 쓴다.
- **관리자 페이지(`frontend/admin/`)**: 모니터링 대시보드(공개 공연 수 / 오늘 확정 예매
  건수 / 전체 미판매 좌석 수 / 누적 매출 KPI + 공연별 회차별 좌석 판매 현황), 직원 아이디
  발급, 회원 상태 변경, 전체 예약 조회, 티켓 차단. `IsAdmin` 권한이 걸린 `/api/admin/*`
  API만 쓴다.
- 두 페이지 모두 상단에 간이 로그인 폼이 있다(`POST /api/auth/login/`) — 별도 인증
  페이지를 아직 안 만들었으므로 임시 배치한 것이며, 실제 배포 시에는 Bastion을 거친
  관리망에서만 접근 가능하도록 firewalld/HAProxy에서 추가로 막아야 한다(SOC 검토 필요).
- **로컬 개발**에서는 `config/settings.py`의 `STATICFILES_DIRS`가 `frontend/`를 직접
  가리키도록 이미 설정해뒀다 — 그래서 `python manage.py runserver` 하나만 띄우면
  `/static/staff/index.html`, `/static/admin/index.html`로 API와 화면이 같은 오리진에서
  같이 뜬다(맨 위 "로컬에서 화면 띄우기" 참고). 별도 서버나 CORS 설정이 필요 없다.
- **실제 배포(WEB/WAS Zone)**에서는 nginx가 `frontend/`를 정적 파일로 서빙하고 `/api/`만
  WAS Zone으로 리버스 프록시한다 — 로컬 개발용 `STATICFILES_DIRS` 설정과는 별개다.

## 팀 공유 DB에 실제로 연결하기 (SQLite → MariaDB 전환)

지금까지의 "로컬에서 화면 띄우기"는 `db.sqlite3`라는 **나만의 로컬 파일**에 쓰고
읽는다. 로그인이 되고 화면이 뜨는 건 Django 코드 자체가 정상이라는 증거는 되지만,
**팀 공유 DB(다른 조원 PC 또는 최종 db-master 10.10.1.2)에 실제로 데이터가
등록되는지는 전혀 증명하지 못한다.** 그걸 확인하려면 아래처럼 연결 대상만
바꿔주면 된다 — 코드는 한 줄도 손댈 필요 없다.

```bash
# 1) .env 생성 (한 번만)
cp .env.example .env

# 2) .env 안에 아래 값을 채운다 (DB를 들고 있는 조원에게 IP/계정정보를 받아서)
#    DB_ENGINE은 안 적어도 된다 — 기본값이 이미 mysql이다.
DB_HOST=<DB를 들고 있는 조원 PC의 사설 IP>
DB_PORT=3306
DB_NAME=linkticket
DB_USER=linkticket_app
DB_PASSWORD=<받은 비밀번호>

# 3) 그 다음부터는 명령어가 완전히 동일하다
python manage.py migrate
python manage.py runserver
```

`config/settings.py`는 기본값 자체가 MariaDB(mysql 엔진)다 — `.env`에 위 4개 값만
채우면 곧바로 그 DB에 연결된다. `DB_ENGINE=sqlite`는 DB 서버 없이 화면만 잠깐 보고
싶을 때만 쓰는 예외 opt-in이고, 기본 동작이 아니다. `.env`는 `.gitignore`에 포함돼
있어 git에 올라가지 않으므로 비밀번호를 커밋할 위험이 없다.

### "DB 컴퓨터에서 확인해야 하는가?" — 아니다. 다만 조건이 있다

물리적으로 그 PC 앞에 앉아있을 필요는 없다. 필요한 건 **네트워크로 그 PC의 MariaDB
포트(3306)에 도달 가능한지**와 **그 계정에 원격 접속 권한이 있는지** 두 가지뿐이다.
MariaDB는 기본 설정(`bind-address=127.0.0.1`)에서는 로컬호스트 접속만 받고, 계정도
기본은 `'user'@'localhost'`로 생성되기 때문에 **DB를 들고 있는 조원이 먼저 아래 두 가지를
열어줘야** 다른 팀원 PC에서 붙을 수 있다.

DB를 들고 있는 조원의 PC(CentOS Stream 9 기준)에서:

```bash
# (1) MariaDB가 외부 인터페이스에서도 듣도록 설정
#     /etc/my.cnf.d/mariadb-server.cnf (또는 해당 include 파일)
[mysqld]
bind-address=0.0.0.0        # 팀 내부망 전용이면 해당 인터페이스 IP로 좁혀도 됨

# 설정 반영
sudo systemctl restart mariadb

# (2) 최소권한 원칙에 따라 "내 IP만" 3306을 허용 (전체 개방 금지)
sudo firewall-cmd --permanent --zone=public \
  --add-rich-rule='rule family="ipv4" source address="<내 PC의 사설 IP>/32" port protocol="tcp" port="3306" accept'
sudo firewall-cmd --reload

# (3) 해당 IP에서만 접속 가능한 계정 발급 (root 권한 계정을 그대로 공유하지 않는다)
mysql -u root -p
> CREATE USER 'linkticket_app'@'<내 PC의 사설 IP>' IDENTIFIED BY '<비밀번호>';
> GRANT ALL PRIVILEGES ON linkticket.* TO 'linkticket_app'@'<내 PC의 사설 IP>';
> FLUSH PRIVILEGES;
```

같은 사설망(팀 회의실 와이파이, 학교 랩실 LAN 등)에 있다면 이걸로 끝이다. 만약 서로
다른 네트워크(재택 등)라 3306에 직접 도달이 안 되면, 방화벽을 열기보다는 SSH 터널을
쓰는 편이 안전하다(Zero Trust 원칙상 DB 포트를 인터넷에 직접 노출하는 것보다 낫다):

```bash
# DB를 들고 있는 조원 PC에 SSH 계정이 있다면
ssh -L 3306:127.0.0.1:3306 <조원계정>@<조원 PC의 공인/VPN IP>
# 이 터널이 떠 있는 동안은 .env의 DB_HOST=127.0.0.1 로 그대로 접속된다
```

주의할 점 — **스키마(테이블 구조) 자체가 어긋나 있으면 연결이 되어도 의미가 없다.**
`python manage.py migrate`는 "내가 가진 migrations 파일" 기준으로 테이블을 만들거나
바꾼다. 만약 DB를 들고 있는 조원이 이 스켈레톤과 다른 자기 모델로 이미 `migrate`를
돌려서 테이블을 만들어놨다면, 내가 접속해서 `migrate`를 돌리는 순간 컬럼 불일치로
에러가 나거나, 최악의 경우 에러 없이 조용히 다른 스키마 위에 얹혀서 데이터가 깨질 수
있다. 그래서 **공유 DB에 연결하기 전에 반드시 팀 채팅으로 "지금 DB 스키마가 이
스켈레톤의 `migrations/0001_initial.py` 기준이 맞는지"부터 확인**해야 한다. 다음
섹션(팀원 코드 반영)에서 이 문제를 정면으로 다룬다.

## Git에 올릴 때 — 어떤 파일을 커밋할지 / 브랜치 전략 / merge 순서

### 1) 무엇을 커밋하는가

이 zip 안 파일은 전부 커밋 대상이다 — `.gitignore`가 이미 "커밋하면 안 되는 것"만
걸러주므로, 그냥 전체를 `git add`하면 된다.

```bash
cd linkticket_skeleton   # 이미 팀 저장소(git init/clone된 폴더) 안이라고 가정
git status               # 뭐가 새로 생겼는지 먼저 눈으로 확인 — 무지성 add 금지
git add .
git status               # add 후 다시 한번 확인 (아래 체크리스트와 대조)
```

**반드시 커밋에 포함되어야 하는 것** (이게 빠지면 팀원이 받았을 때 안 돌아간다):
- `manage.py`, `config/`(`settings.py`, `wsgi.py`, `urls.py`, `__init__.py`) — 방금 만든
  `config/__init__.py`(PyMySQL shim)도 포함
- 각 앱 폴더 전체: `models.py`, `serializers.py`, `services.py`, `views.py`, `urls.py`,
  `apps.py`, `__init__.py`
- **`migrations/0001_initial.py` — 특히 이걸 빠뜨리는 실수가 흔하다.** `.gitignore`에
  `migrations/`를 넣는 사람들이 있는데, 그건 라이브러리/템플릿 저장소에서나 하는 것이고
  이 프로젝트처럼 **팀 전체가 같은 스키마를 공유해야 하는 경우 migrations는 코드다.**
  커밋하지 않으면 팀원이 `migrate`를 돌려도 테이블이 하나도 안 생긴다.
- `frontend/` 전체 (직원/관리자 페이지)
- `requirements.txt`, `.env.example`, `.gitignore`, `README.md`

**커밋하면 안 되는 것** (이미 `.gitignore`가 자동으로 막아줌 — `git status`에 안 보이면
정상):
- `.venv/`, `__pycache__/`, `*.pyc`
- `db.sqlite3` — 내 로컬 테스트 데이터일 뿐, 팀 공유 대상이 아니다
- `.env` — DB 비밀번호가 들어있는 실제 값. **절대 커밋 금지.** (`git status`에 `.env`가
  보인다면 `.gitignore`가 왜 안 먹는지부터 확인하고, 이미 커밋된 적이 있다면 비밀번호를
  즉시 변경해야 한다 — git 히스토리에서 지워도 예전 커밋에는 남아있기 때문)

### 2) 브랜치 전략 — 5인 팀 기준

지금 상황(스켈레톤은 이미 공유했는데 팀원들이 각자 브랜치/커밋 없이 따로 만든 상태)을
정리하려면, "각자 브랜치 → PR → 코드리뷰 후 병합" 구조로 지금이라도 전환하는 게 맞다.
`main`(또는 `develop`)에 아무나 바로 push하는 방식은 지금 겪고 있는 문제(다들 자기
스타일대로 만들어서 이름이 다 갈라지는 것)를 구조적으로 막지 못한다.

```bash
# 최신 main을 받고
git checkout main
git pull origin main

# 내 담당 영역(SOC/Admin) 기준으로 브랜치를 딴다 — 접두사로 담당자/영역을 구분
git checkout -b feat/soc-admin-staff-pages

# 작업 후
git add .
git commit -m "feat(dashboard,frontend): 관리자 모니터링 대시보드 + 직원/관리자 페이지 추가"
git push -u origin feat/soc-admin-staff-pages
```

브랜치 네이밍은 팀 컨벤션이 없다면 `feat/<영역>-<기능>`, `fix/<영역>-<버그>` 정도로
통일해서 제안해라(예: `feat/was-python-app-reservation`, `fix/db-schema-payment`).
그 다음 GitHub/GitLab에서 `feat/soc-admin-staff-pages → main`(또는 `develop`)으로 **PR을
연다.** PR 설명에는 반드시 "이 스켈레톤/네이밍 컨벤션 문서 기준으로 작성했음"을
명시해서, 리뷰어(다른 팀원)가 비교 기준을 알 수 있게 한다.

### 3) merge 순서 — 왜 순서가 중요한가

이 프로젝트는 앱 간 의존 방향이 고정되어 있다(위 "앱 간 의존 방향" 다이어그램 참고):
`accounts → catalog → reservations → {payments, tickets, coupons}`, `dashboard`는
나머지 전체를 read-only로 참조. **이 의존 순서대로 merge해야 충돌을 일찍, 작게
발견한다.** 반대로 하면(예: `payments`를 먼저 merge하고 그 다음 `accounts`를 손대면)
아직 존재하지 않는 모델을 참조하는 import 에러가 뒤늦게, 더 큰 범위로 터진다.

```
1. accounts        (다른 모든 앱이 Member를 참조하므로 항상 최우선)
2. catalog
3. reservations
4. payments / tickets / coupons  (reservations에 의존, 서로는 독립적이라 병렬 가능)
5. events / notices               (accounts에만 의존, 독립적이라 아무 때나 가능)
6. dashboard                      (나머지 전체가 merge된 뒤 마지막)
7. frontend/                      (API가 실제로 존재해야 화면에서 호출 가능하므로 마지막)
```

merge 직전에는 항상 최신 main을 내 브랜치로 먼저 끌어와서(`rebase` 또는 `merge`) 로컬에서
충돌을 해결한 뒤 push하는 걸 원칙으로 해라:

```bash
git checkout feat/soc-admin-staff-pages
git fetch origin
git rebase origin/main       # 충돌나면 여기서 해결 (merge보다 히스토리가 깔끔함)
# 충돌 해결 후
git add <충돌났던 파일>
git rebase --continue
git push --force-with-lease origin feat/soc-admin-staff-pages   # rebase 후에는 --force 필요
```

`--force`가 아니라 **`--force-with-lease`를 쓰는 이유**: 내가 모르는 사이 원격 브랜치에
누가 다른 커밋을 push했다면 `--force-with-lease`는 실패하며 알려주지만, `--force`는
그 커밋을 그냥 덮어써서 조용히 날려버린다. 팀 작업에서 `git push --force`는 지양해라.

## DB 담당자 혼자 스켈레톤과 다르게 만든 상태를 어떻게 정리하는가

**중요한 정정: 이건 "5명이 각자 다르게 짠 코드를 조율하는" 일반적인 병합 문제가
아니다.** accounts/catalog/reservations/payments/tickets/coupons/events/notices/
dashboard — 즉 애플리케이션 코드를 담당하는 4명은 이미 스켈레톤과 네이밍 컨벤션
문서를 그대로 따라갔다. 어긋난 건 **DB 파트 담당자 한 명이 물리적 DB 스키마를
독자적으로 만든 것 하나뿐**이다. 범위가 훨씬 좁고 명확하므로, 앞서 설명한 "여러
사람의 코드 스타일을 다 대조해서 리팩터링"하는 수준의 작업이 아니라 **DB 스키마
하나를 팀이 확정한 `migrations/0001_initial.py` 기준에 맞추는 작업**으로 좁혀진다.

이 문제가 특히 까다로운 이유(SOC/Admin 관점에서 짚어야 할 부분)는, **DB 스키마
불일치는 코드 리뷰로는 절대 못 잡는다**는 데 있다. 나머지 4명이 전부 로컬 SQLite로
`python manage.py migrate` → `runserver` → 화면 확인까지 그린라이트를 받아도, 그건
"내가 만든 `models.py`와 내 로컬 SQLite가 서로 맞는다"는 증명일 뿐이지 "DB 담당자의
실제 MariaDB와도 맞는다"는 증명이 전혀 아니다. 이 사실은 실제로 공유 DB에 연결을
시도하는 순간(위 "팀 공유 DB에 실제로 연결하기" 절차)에야 `django.db.utils
.OperationalError` 또는 `ProgrammingError`(예: `Unknown column 'member_id' in
'field list'`)로 드러난다. 즉 지금 이 문제를 merge 전에, 실서비스 데이터가 쌓이기
전에 발견한 게 오히려 다행인 타이밍이다.

### 처리 순서 1 — 먼저 확인할 것: 아직 버려도 되는 데이터인가

DB 담당자에게 물어볼 첫 질문은 "그 DB에 지우면 안 되는 실 데이터가 있는가"다. 이
답에 따라 아래 두 경로가 완전히 갈린다.

**경로 A — 테스트용이라 지워도 되는 경우 (지금 시점에는 대부분 이쪽일 가능성이 높다):**
가장 깨끗한 해결책은 DB 담당자가 자기가 만든 스키마를 버리고, 팀이 확정한
`migrations/0001_initial.py`로 다시 만드는 것이다. DB 담당자의 PC(CentOS Stream 9,
MariaDB)에서:

```bash
mysql -u root -p -e "
DROP DATABASE IF EXISTS linkticket;
CREATE DATABASE linkticket CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
"

# 이 zip의 skeleton을 그대로 받아서
cd linkticket_skeleton
cp .env.example .env        # DB_ENGINE=mysql, DB_HOST=127.0.0.1(자기 자신) 등으로 채움
python manage.py migrate    # 팀 확정 migrations 기준으로 테이블이 새로 생성된다
```

이렇게 하면 "DB 담당자가 직접 스키마를 짠다"는 행위 자체가 없어진다 — **DB 담당자도
스키마를 손으로 설계하는 게 아니라, 이 스켈레톤의 `migrate`를 그대로 실행하는 것으로
역할이 바뀐다.** 이건 원래 이 스켈레톤을 만든 목적(이름/구조 해석 편차 제거)과도
정확히 일치한다 — DB 스키마도 예외가 아니다.

**경로 B — 이미 지우면 안 되는 데이터가 들어가 있는 경우:**
스키마를 갈아엎을 수 없다면, 실제 스키마를 코드로 뽑아서 팀 기준과 필드 단위로
대조한 뒤 변경 마이그레이션을 새로 작성해야 한다.

```bash
# DB 담당자 PC에서 — 지금 DB의 실제 테이블 구조를 Django 모델 코드로 역추출
python manage.py inspectdb > actual_schema_dump.py
```

이 `actual_schema_dump.py`와 스켈레톤의 각 앱 `models.py`를 필드 단위로 나란히
대조해서 "이름이 다른 컬럼"만 골라낸다(예: DB 담당자가 `user_id`로 만들었는데
컨벤션은 `member_id`, 또는 테이블명이 `reservations`인데 컨벤션은 `reservation`
단수형). 다른 부분이 확정되면, 데이터를 보존하면서 컬럼/테이블명만 바꾸는
마이그레이션을 새로 만든다:

```bash
python manage.py makemigrations accounts --empty --name align_member_id_with_convention
```

```python
# accounts/migrations/000X_align_member_id_with_convention.py
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [("accounts", "0001_initial")]
    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE user RENAME COLUMN user_id TO member_id;",
            reverse_sql="ALTER TABLE user RENAME COLUMN member_id TO user_id;",
        ),
    ]
```

`RunSQL`을 쓰는 이유는 Django의 `RenameField`가 모델 정의 히스토리까지 함께
추적해야 해서 이미 `inspectdb`로 역생성한 모델과 어긋나기 쉽기 때문이다 — 실제
운영 DB에 데이터가 있는 상태에서의 컬럼 rename은 `RunSQL`로 명시적인 SQL을 직접
실행하는 편이 뭐가 일어나는지 예측 가능하고 안전하다. 이 방식은 컬럼/테이블 몇 개
수준일 때는 현실적이지만, 대조 결과 어긋난 필드가 많다면(예: 10개 이상) 사실상
경로 A와 비용이 비슷해지므로, 그 시점에는 "지금 데이터를 정말 못 버리는지"를 한 번
더 팀에 확인하는 게 낫다.

### 처리 순서 2 — 애플리케이션 코드(models.py 등)까지 어긋났는지 별도 확인

DB 담당자가 손댄 게 순수하게 물리적 MariaDB 스키마뿐인지, 아니면 자기 나름대로
`accounts/models.py` 같은 Django 모델 파일까지 따로 만들었는지도 확인해라. 후자라면
이건 스키마 문제가 아니라 코드 문제이므로, 위 SQL 레벨 작업과는 별개로 해당 파일만
스켈레톤의 `models.py` 기준으로 되돌려야 한다(git 기준으로는 그 브랜치의 해당 파일만
스켈레톤 버전으로 덮어쓰고, DB 담당자가 짠 로직 중 살릴 게 있으면 함수 단위로
옮기는 정도지, 이번 경우는 애초에 DB 스키마/설정 문제일 가능성이 높으므로 코드
자체의 충돌은 크지 않을 것이다).

### 처리 순서 3 — 프로세스 관점: "요청"이 아니라 "이미 확정된 산출물"로 접근

지금 상황을 개인 간 설득으로 풀려고 하면 다시 같은 일이 반복될 수 있다. SOC/Admin
담당으로서 쓸 수 있는 레버리지는, 이 스켈레톤과 네이밍 컨벤션 문서가 "내 개인
의견"이 아니라 **팀 전체가 이미 합의하고 4명이 실제로 따라간 확정 산출물**이라는
사실 자체다. DB 담당자에게 개별적으로 "네가 틀렸다"를 설득하기보다, 팀 채널에 (1)
지금 4명은 이 migrations 기준으로 맞춰져 있고 (2) 공유 DB에 연결해보니 스키마가
달라서 실제 등록 테스트가 막혀 있다는 사실을 공유하고, 위 경로 A/B 중 어느 쪽으로
갈지를 팀 결정으로 만들어라 — 그러면 "내가 시켜서"가 아니라 "팀이 확정한 절차"가
되어 재발 가능성이 줄어든다. 작업계획서/보고서 관점에서도 이 경위(발견 시점, 원인,
선택한 해결 경로, 재발 방지책)를 한 문단으로 기록해두면 나중에 팀 평가에서 "왜
일정이 밀렸는지"에 대한 근거 자료가 된다.

### 처리 순서 4 — 정리 후 검증

DB 담당자가 경로 A 또는 B로 스키마를 맞춘 뒤에는, 반드시 아래 두 단계로 검증해라:

1. **DB 담당자 본인 PC에서**: `python manage.py migrate`가 에러 없이 끝나고,
   `python manage.py check`가 통과하는지.
2. **너(SOC/Admin)를 포함한 다른 팀원 PC에서**: 위 "팀 공유 DB에 실제로 연결하기"
   절차대로 `.env`의 `DB_HOST`를 DB 담당자 PC IP로 맞추고, 실제로 로그인 →
   공연/회차/좌석 등록 → 대시보드 조회까지 끝까지 돌려서 데이터가 실제로 그
   공유 DB에 등록되는지 확인. 이 2번이 통과해야 "우리 팀 전체가 같은 DB, 같은
   스키마로 동작한다"는 증명이 끝난다 — 1번만으로는 DB 담당자 혼자만의 검증이다.

## 다음 단계

- [ ] 운영 배포용 `config/settings.py`를 별도로 작성(SQLite→MariaDB, `DEBUG=False`,
      `SECRET_KEY`/DB 비밀번호를 Ansible Vault로 분리) — 지금 들어있는 `settings.py`는
      로컬 화면 확인 전용이다.
- [ ] 이 스켈레톤과 짝을 이루는 **"LINKTICKET 네이밍 컨벤션 규칙"** 문서(별도 산출물)를
      항상 함께 참조 — 함수 시그니처 표, 클래스 네이밍 규칙, URL name= 규칙이 이 코드와
      1:1로 매칭되어야 한다(12장에 이번 직원/관리자 페이지 반영분이 추가되어 있다).
- [ ] `frontend/staff/`, `frontend/admin/`의 간이 로그인 폼을 실제 인증 플로우(세션 만료
      처리, 관리망 IP 제한 등)로 보강 — 현재는 프로토타입 수준이다.
- [ ] 관리자 대시보드의 매출/미판매 좌석 집계 쿼리(`dashboard/services.py`)는 공연/회차
      수가 커지면 N+1 쿼리가 될 수 있다 — 운영 반영 전 `select_related`/캐싱 검토 필요.

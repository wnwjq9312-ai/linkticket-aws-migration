# 배포 후 기능 수정 및 운영 사용 가이드

검증일: 2026-10-01. 대상 브랜치: `frontend-integration`.

## 수정 내용

- 로그인 기본 이동 위치는 `/`이다. 외부 도메인 `next`는 허용하지 않는다.
- 마이페이지 프로필 조회가 관련 없는 NFT 테이블을 먼저 조회하지 않도록 섹션별로 조회한다. 기존 장애는 `digital_collectible.source_event_id` 부재였다. 운영 NFT 연결 기능은 스키마 정합성 확인 전 명시적으로 준비 중 상태다. 예매/티켓/쿠폰/회원정보 조회는 분리했다.
- 기존 `member` 테이블과 인증을 연결하고 로그인 시 기존 비밀번호 해시나 없는 `last_login` 컬럼을 갱신하지 않는다.
- `birth_date`: `DateField(null=True, blank=True)` / DB `DATE NULL`.
- `gender`: `CharField(max_length=10, null=True, blank=True)` / DB `VARCHAR(10) NULL`. 저장값은 `M`/`F`, 화면은 남/여. 미입력은 NULL. 미래 생년월일과 허용되지 않은 성별은 거부한다.
- 생년월일/성별 컬럼은 DB 담당자가 추가했다. 이번 애플리케이션 작업은 ALTER 또는 migrate를 실행하지 않았다. Slave 복제 확인은 DB 담당자가 별도 수행한다.
- 공지 DB의 `chk_notice_type`은 `공지/이벤트/안내/점검`을 허용한다. 모델은 이 저장값을 사용하며 serializer가 기존 API 코드 `NOTICE/EVENT/GUIDE/MAINTENANCE`와 양방향 변환한다. DB 제약조건과 기존 공지는 변경하지 않았다.
- 달력 셀의 공통 button 좌우 padding을 제거하고 가로 숫자/한 줄 표시를 고정했다. 전체 메인 레이아웃은 유지한다. CSS URL 버전으로 기존 브라우저 캐시를 갱신한다.

## 세션

운영 `SESSION_ENGINE=django.contrib.sessions.backends.cached_db`, `SESSION_CACHE_ALIAS=sessions`.

Redis 공유 캐시 + `django_session` DB 보관을 함께 사용한다. 순수 Redis 전용 세션이 아니다. 이전 DB 세션과의 호환성을 유지한다.

- Redis 서버: `10.10.2.6:6379`.
- 세션 논리 DB: 양쪽 WAS에서 `SESSION_REDIS_DB=0`.
- prefix: `linkticket:sessions` (Django 버전 prefix와 세션 backend prefix가 뒤에 붙는다).
- 일반 `REDIS_URL`의 DB 번호는 서버마다 달랐다. 세션 URL만 DB 0으로 명시적으로 정규화하고 일반 Redis 설정/데이터는 보존했다.
- 실제 로그인 키 생성, 두 WAS 인증 유지, 다른 WAS에서 로그아웃, Redis/DB 세션 제거, 이전 쿠키 재사용 거부를 확인했다. FLUSH는 실행하지 않았다.

## 계정 및 권한

| 역할 | `/dashboard/` | `/staff/` | 관리 API |
|---|---|---|---|
| 비로그인 | 로그인 이동 | 로그인 이동 | 인증/권한 거부 |
| USER | 403 | 403 | 관리자/직원 API 403 |
| STAFF | 403 | 200 | 직원 API 허용, 관리자 API 거부 |
| ADMIN | 200 | 200 | 관리자/직원 API 허용 |

새 계정 `admin`(ADMIN), `staff_test`(STAFF)을 생성했다. 기존 계정 승격/초기화는 하지 않았다. 비밀번호는 Django 해시로 저장한다. 초기 비밀번호는 WAS-1 root 전용 디렉터리에 보관하며 Git/보고서에 포함하지 않는다.

새 역할 계정을 추가할 때는 운영 환경변수를 안전하게 로드한 동일 Python 환경에서 다음 관리 명령을 사용한다. 비밀번호는 숨김 프롬프트에서 입력한다. 이미 존재하는 계정에는 동작하지 않는다.

```bash
python manage.py provision_member --username NEW_LOGIN_ID --email ACCOUNT_EMAIL --role STAFF --name '직원 이름'
```

이미 만든 `admin`에 위 명령을 다시 실행하지 않는다. 인증정보 확인/변경은 서버 관리자에게 요청한다.

## 사용 방법

1. `https://www.linkticket.com/login/`에서 역할 계정으로 로그인한다.
2. 관리자: `/dashboard/`. 직원: `/staff/`. 두 화면은 서버에서도 역할을 검증한다.
3. 직원 화면의 공지사항 탭에서 유형/제목/본문/공개 상태를 입력하고 등록한다. 공개 공지는 `/notices/`에서 확인한다. 현재 이미지 없는 공지 등록을 운영 DB까지 검증했다. 이미지 업로드는 media NFS 준비 전 사용하지 않는다.
4. 직원 화면에는 공연/회차/좌석 관리와 QR 검표 UI/API도 구현되어 있다. 이번 검증에서 실제 공연·좌석 변경이나 티켓 상태 변경은 수행하지 않았다.
5. 관리자 화면에는 통계, 직원/회원 조회 및 직원 생성, 회원 상태 관리, 예매 조회 기능이 구현되어 있다. 통계·회원 조회 GET을 검증했으며 기존 회원 상태를 변경하지 않았다. NFT/coupon/reward 관련 쓰기와 스키마 호환성은 별도 확인이 필요하다.
6. 사용자 Mock 흐름은 공연 상세 → 날짜/좌석 → 결제 → `DEMO` 승인 코드 → 완료 → 마이페이지 예매 내역이다. 실제 PG 승인, 실제 예약/결제 DB INSERT가 아닌 세션 기반 Mock 영수증이다.

## 검증 결과

- 로컬 테스트 51개 통과(50개 전체 실행 + 신규 공유 세션 설정 테스트 1개 별도 실행). 운영 Django check 오류 0.
- 실제 HTTP 회원가입 → 생년월일/성별 저장 → 로그인 302 `/` → 메인/마이페이지 200.
- 기존 회원 15명의 프로필/예매/티켓/쿠폰: 60개 읽기 전용 렌더링 200.
- 운영 VIP HTTPS 경로 로그인 → 공연/좌석 → Mock 결제 → 완료 → 마이페이지 → 로그아웃 통과. TLS hostname 검증 유지.
- STAFF 공지 INSERT, author FK, 유형/본문/공개 상태 및 사용자 목록 표시 확인.
- 기존 회원 15건의 모든 컬럼 값 해시 비교 일치. 신규 ADMIN/STAFF/검증 USER만 추가되어 총 18건. payment 기존 1건 유지.
- HTTPS 핵심 페이지 200, 참조 static 27개 모두 200.
- 달력은 운영 공개 HTML을 로컬 렌더링한 Edge에서 1920/1440/1280/1024/768/390/1920px 검증. 숫자 세로 표시·셀 넘침·문서 가로 넘침·JS 오류 없음. 이 검증은 자동화 브라우저의 운영 인증서 검증을 대신하는 것이 아니다.

## 배포 및 복구

- 신규 release: `/opt/linkticket/releases/linkticket-20261001-postdeploy/` (기존 검증된 venv를 재사용).
- 기존 release: `/opt/linkticket/releases/linkticket-20260930-211208/` 보존.
- 보호된 운영 env: `/etc/linkticket/releases/linkticket-20260930-211208.env` 유지.
- WAS-1 `gunicorn.service`: `10.10.2.2:8000`.
- WAS-2 `ticket_app.service`: `10.10.2.4:8080`.
- 각 WAS 백업: `/var/backups/linkticket/postdeploy-20261001/`의 `90-linkticket-release.conf`, `production.env`, `member-baseline.json`.
- 각 WEB CSS 백업: `/var/backups/linkticket/postdeploy-20261001/ui3.css`.
- WEB Nginx/Proxy/HAProxy/라우터/firewall/포트/DNS/TLS는 변경하지 않았다.

복구는 해당 WAS의 기존 drop-in 백업을 `/etc/systemd/system/<해당 unit>.d/90-linkticket-release.conf`에 복사하고 `systemctl daemon-reload` 후 해당 unit만 한 대씩 restart한다. 정상 HTTP 확인 후 다음 WAS를 복구한다. WEB은 백업 CSS를 기존 static `linkticket/ui3.css`로 복원한다. DB 컬럼/계정/기존 데이터/백업을 삭제하는 복구는 수행하지 않는다. 기존 코드로 복구하면 이번에 해결한 마이페이지 장애가 다시 나타날 수 있다.

## 남은 이슈

- 운영 migration history 및 모델/기존 migration 불일치는 해결한 것으로 간주하지 않는다. 운영에서 `migrate`, `--fake`, `--fake-initial`을 실행하지 않는다.
- payment.updated_at, notice 모델/과거 migration 등 기존 차이가 남는다. 이번 공지 유형 저장 오류는 API↔DB 매핑으로 해결했다.
- NFT relation/favorite, coupon/reward 전체 쓰기 스키마, media/NFS, 실제 PG는 별도 작업이다. 일반 프로필/예매 조회 실패와 분리했다.
- 이 프로젝트 도메인은 내부 시연 환경이다. 다른 PC는 내부 DNS 및 내부 CA 신뢰 준비가 필요하다.

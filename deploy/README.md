# LINKTICKET 수동 온프레미스 배포 준비

이번 변경은 코드 준비이며 실제 서버 배포 완료가 아니다. UI·Mock 결제·기존 모델과 migration은 보존했다. CI/CD는 추가하지 않았다.

## 반영 내용

- `config.settings_production`: DEBUG=False, 필수 secret/hosts/CSRF 검사, DB 경로를 MaxScale 10.10.2.5:4006 및 ticketing_db/ticket_app으로 검증. 개발 서버는 기존 settings를 계속 사용한다.
- 일반 업로드는 WEB NFS, NFT 업로드는 별도 NFT_MEDIA_ROOT와 /nft-media/ URL로 분리. DB image_path 값은 기존 `nft/파일명` 상대 경로 유지. 모델·스키마 변경 없음.
- 파일 저장 전 지정 mount 존재 여부와 저장 경로 포함 여부를 검사. 이는 실제 NFS 서버 주소/Export/권한 확인을 대체하지 않는다. NFS 서버 불응 시 I/O 지연은 운영 mount 정책에 따른다.
- Gunicorn 실행 설정 및 systemd 예시, WEB Nginx 병합용 예시, 읽기 전용 DB 메타데이터 수집 도구 추가.
- Python 3.9 호환 범위 요구사항을 별도 파일로 제공. 기존 개발 requirements는 유지.

## 확정되지 않은 운영 정보

서비스 도메인/인증서, 기존 서비스 사용자, WEB NFS source와 두 WAS의 mount, DB NFS 접근 허용 정책과 mount, NFT 읽기 제공 경로, 공용 Redis, 실제 DB schema 및 migration 이력이 필요하다. 비밀 값은 서버의 보호된 환경 파일에 직접 입력한다.

요청서 DB NFS 허용 10.10.1.0/24에는 WAS 두 대가 없다. NFS export·firewall·routing·Masquerade·Replication 설정은 변경하지 않았다. `/nfs/db_backup` 전체는 웹에 공개하면 안 된다. NFT 전용 하위 디렉터리를 사용하고 읽기 제공 방식을 확인할 때까지 Nginx 예시의 /nft-media/는 503으로 닫아 두었다. 따라서 이 예시를 그대로 운영 완료 구성으로 간주하지 않는다.

## 서버별 적용 순서 (현재는 검토용, 한꺼번에 실행하지 않음)

### [WAS-1 / 10.10.2.2]

1. 기존 checkout 상태, Python 3.9.25, mount, service/port를 읽기 전용으로 확인한다.
2. 깨끗한 checkout에서 원격 frontend-integration의 검토한 커밋을 배치한다. 로컬 개발 스냅샷의 synthetic Git 이력은 push하지 않는다.
3. 기존 venv를 덮어쓰지 않고 릴리스용 venv에 `python3.9 -m pip install -r deploy/requirements-py39.txt`로 설치 후 `pip check`와 버전 목록을 보관한다. 이 명령은 대상 서버에서 아직 실행되지 않았다.
4. `onprem.env.example`을 기준으로 /etc/linkticket/linkticket.env에 실제 값을 운영자가 입력한다. 파일 mode 0600. systemd EnvironmentFile 형식이며 shell source와 동일한 문법으로 가정하지 않는다. Django CLI 실행에도 승인된 방식으로 같은 환경을 주입한다.
5. `python manage.py check --deploy`, `python deploy/inspect_database.py`, `python manage.py showmigrations`, `python manage.py migrate --plan` 결과를 검토한다. 아직 migrate는 실행하지 않는다.
6. DB 백업·실제 DDL·기존 데이터 영향·복제 상태 검토 후 필요한 migration만 MaxScale 경유로 한 번 적용한다. 자동 --fake, 데이터 초기화, destructive migration은 금지.
7. `python manage.py collectstatic --noinput` 결과 STATIC_ROOT를 WEB로 복사한다. static 원본/templates를 정적 HTML로 대체하지 않는다.
8. 기존 unit과 비교한 뒤 Gunicorn config.wsgi:application을 10.10.2.2:8000에서 실행한다. 실제 LISTEN/HTTPS 프록시 경유 기능을 확인한다.

NFS 운영 경로를 채울 때 MEDIA_ROOT와 NFT_MEDIA_ROOT는 각각 확인된 mount 내 서비스 전용 하위 디렉터리로 지정한다. 기존 media/nft 파일은 NFT_MEDIA_ROOT/nft/로 복사하여 개수·해시·권한·조회 확인 후 전환한다. 원본을 지우지 않는다. 일반 업로드도 기존 상대경로를 유지한다. 두 WAS에서 동일한 DB, secret, media, NFT, Redis 설정을 공유한다.

### [WAS-2 / 10.10.2.4]

WAS-1 검증 후 동일 커밋/의존성/env/mount를 배치하되 GUNICORN_BIND=10.10.2.4:8080 사용. migration을 다시 따로 적용하지 않는다. 기존 데이터/세션/업로드를 두 WAS에서 같은 값으로 조회하는지 검증한다.

### [WEB-1 / 10.10.4.101]

collectstatic 결과를 /var/www/linkticket/에 배치. 기존 TLS vhost에 web-nginx.conf.example의 내용을 검토하여 병합하고 nginx -t 통과 후 reload한다. 예시 placeholder와 NFT 503을 해소하기 전 서비스 전환 금지. WEB가 X-Forwarded-Proto를 덮어쓰도록 유지하고 WAS 직접 접근은 기존 신뢰 WEB 정책을 확인한다. 실제 사용자 IP 복원은 기존 trusted proxy 정책을 검토한 후 수행한다.

### [WEB-2 / 10.10.4.102]

같은 static 파일과 검토된 vhost/NFS 경로로 배치. WEB-1과 각각 이미지·동적 URL 응답을 비교한다. 기존 설정 전체를 덮어쓰지 않는다.

### [Proxy01 / 10.10.5.2]

기존 upstream이 https://10.10.4.101:443 및 https://10.10.4.102:443인지 확인. WAF, Host 전달, upstream TLS 인증서/SNI 검증은 유지한다. 정상 설정은 변경하지 않는다.

### [Proxy02 / 10.10.5.3]

Proxy01과 동일한 읽기 전용 확인부터 진행한다.

### [MaxScale / 10.10.2.5]

기존 Read-Write-Service와 4006 Listener, backend 상태를 확인한다. 설정 변경 없음.

### [DB Master / 10.10.1.2]

기존 schema/engine/backup 정책을 조회. 권한 있는 계정의 보호된 옵션 파일로 일관된 백업을 생성하고 검증한 뒤 migration을 검토한다. Django DB 연결을 Master 직접 주소로 바꾸지 않는다.

### [DB Slave01 / 10.10.1.3]

migration 전후 Slave_IO_Running, Slave_SQL_Running, Seconds_Behind_Master, Last_IO_Error/Last_SQL_Error 및 변경 schema를 확인. migration 실행 없음.

### [DB Slave02 / 10.10.1.4]

Slave01과 동일 검증. 복제 설정 변경 없음.

### [DB NFS / 10.10.1.5]

현재 export, mount, 디렉터리 권한만 먼저 조회. WAS 쓰기 접근을 허용할 필요가 확인되면 최소 변경안을 먼저 보고한다. 기존 백업 데이터 삭제나 export 재구성은 하지 않는다.

## 검증과 한계

로컬 Python 3.12.14 / Django 4.2.30에서 테스트 31개 통과. check 오류 0, migration drift 없음, collectstatic 성공. 운영 설정 check --deploy는 HSTS 미설정 경고 1개: 실제 도메인 TLS 검증 전 HSTS를 강제하지 않도록 의도한 기본값이다. secret 누락, 직접 Master 주소, wildcard host 시작 거부 검증. Python 3.9 문법 파싱 통과; Python 3.9 서버 실행·의존성 설치·Gunicorn/Linux·Nginx 구문·MariaDB·NFS 실제 쓰기/읽기는 미검증.

Python 3.9 및 Django 4.2는 공식 지원 종료 상태다. 호환 범위 파일은 지원 보장 또는 보안 검증된 lockfile이 아니다. 요청한 런타임을 임의 업그레이드하지 않았다. 공식 정보: https://peps.python.org/pep-0596/ , https://www.djangoproject.com/download/ . 패키지 호환 정보: https://pypi.org/project/gunicorn/23.0.0/ , https://pypi.org/project/djangorestframework/3.16.1/ , https://pillow.readthedocs.io/en/stable/installation/platform-support.html .

실제 PG·Kakao OAuth는 추가하지 않았다. 지도 JS 키와 사이트 도메인은 운영자가 등록한다. 서비스 도메인이 아직 없어 실제 HTTPS/CSRF/OAuth/지도 검증은 완료할 수 없다.

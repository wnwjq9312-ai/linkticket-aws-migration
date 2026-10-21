"""Shared development settings. Production uses config.settings_production."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# .env 파일이 있으면 환경변수로 로드한다. python-dotenv가 설치되어 있지 않아도
# (=아무도 .env를 안 쓰는 개인 로컬 SQLite 확인 상황) 서버가 죽지 않도록 방어한다.
try:
    from dotenv import load_dotenv

    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass

# 개발용 임시 키. 운영에서는 반드시 Ansible Vault로 관리하는 값으로 교체한다.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-insecure-secret-key-change-me")

DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")  # 개발용 기본값

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
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

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "libraries": {"ui": "common.templatetags.ui"},
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "payments.venue_context.common_map",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# 팀 확정 DB는 MariaDB(WAS Zone was-maxscale 10.10.2.5 경유 / DB Zone db-master
# 10.10.1.2)이므로 기본값(DB_ENGINE 미설정 시)도 mysql이다 — SQLite가 기본이 아니다.
# .env에 DB_HOST/DB_NAME/DB_USER/DB_PASSWORD만 채우면 곧바로 그 MariaDB로 붙는다.
DB_ENGINE = os.environ.get("DB_ENGINE", "mysql")

if DB_ENGINE == "sqlite":
    # 예외적으로 DB 서버 없이 화면 UI만 잠깐 보고 싶을 때만 .env에
    # DB_ENGINE=sqlite를 명시적으로 넣어서 쓰는 opt-in 경로. 팀 공유/운영 DB와는
    # 무관한 완전히 별도의 로컬 파일이며, 기본 동작이 아니다.
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    # 필수 항목이 .env에 없으면 여기서 바로 KeyError로 죽는다 — MariaDB 접속 정보를
    # 안 채운 채로 조용히 다른 DB에 쓰는 상황을 막기 위해 일부러 fail-fast로 둔다.
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.environ["DB_NAME"],
            "USER": os.environ["DB_USER"],
            "PASSWORD": os.environ["DB_PASSWORD"],
            "HOST": os.environ["DB_HOST"],
            "PORT": os.environ.get("DB_PORT", "3306"),
            "OPTIONS": {"charset": "utf8mb4"},
        }
    }

AUTH_USER_MODEL = "accounts.Member"
AUTHENTICATION_BACKENDS = ["accounts.backends.ExistingMemberBackend"]

LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True

# 정적 파일 — frontend/를 그대로 서빙해서 별도 서버 없이 화면을 확인할 수 있게 한다.
# DEBUG=True + runserver 조합에서는 collectstatic 없이 STATICFILES_DIRS가 바로 서빙된다.
# 화면은 /staff/, /dashboard/의 Django 템플릿으로 렌더링한다.
# collectstatic 결과는 향후 WEB 서버에서 STATIC_URL 경로로 제공할 수 있다.
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = Path(os.environ.get("STATIC_ROOT", BASE_DIR / "staticfiles"))
KAKAO_MAP_JS_KEY = os.environ.get("KAKAO_MAP_JS_KEY", "")
LOGIN_URL = "/login/"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "common.exception_handler.linkticket_exception_handler",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
}

# 로컬에 Redis가 없어도 서버는 뜬다(redis-py는 실제 명령 실행 시점에만 연결을 시도한다).
# 좌석 임시선점(hold_seat) 계열 API만 Redis가 없으면 에러가 난다.
REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0")

MEDIA_URL = '/media/'
MEDIA_ROOT = Path(os.environ.get('MEDIA_ROOT', BASE_DIR / 'media'))
NFT_MEDIA_ROOT = os.environ.get('NFT_MEDIA_ROOT') or None
NFT_MEDIA_URL = os.environ.get('NFT_MEDIA_URL', MEDIA_URL)

NFT_UPLOADS_ENABLED = True  # Local development; production defaults to disabled.

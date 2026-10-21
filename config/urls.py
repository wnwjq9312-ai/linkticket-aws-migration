"""
프로젝트 루트 URL. 각 앱의 urls.py를 /api/ 하위로 include한다.
참조: 개발 기능 명세서 v2.0 13.3절 API 목록 (모든 API 경로는 /api/ 프리픽스를 갖는다)
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("common.ui_urls")),
    path("booking/", include("payments.ui_urls")),
    path("api/", include("accounts.integration_urls")),
    # Django 기본 관리자 사이트. 명세서의 /api/admin/* (운영 관리 API)와 경로가
    # 겹치지 않도록 /admin-site/로 분리했다.
    # Native admin is deferred: production admin log references auth_user.
    path("api/", include("accounts.urls")),
    path("api/", include("catalog.urls")),
    path("api/", include("reservations.urls")),
    path("api/", include("payments.urls")),
    path("api/", include("tickets.urls")),
    path("api/", include("coupons.urls")),
    path("api/", include("events.urls")),
    path("api/", include("notices.urls")),
    path("api/", include("dashboard.urls")),
]

from django.conf import settings
from django.conf.urls.static import static
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    if settings.NFT_MEDIA_URL != settings.MEDIA_URL:
        urlpatterns += static(settings.NFT_MEDIA_URL, document_root=settings.NFT_MEDIA_ROOT or settings.MEDIA_ROOT)

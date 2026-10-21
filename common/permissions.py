"""
공통 권한 클래스
참조: 개발 기능 명세서 v2.0 11.2절 권한 정책 매트릭스
"""
from rest_framework.permissions import BasePermission

from accounts.models import MemberRole


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.is_active and request.user.role == MemberRole.ADMIN
        )


class IsStaffOrAdmin(BasePermission):
    """QR 검표 등 STAFF/ADMIN 공용 기능. 11.2절 'QR 검표' 행."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_active
            and request.user.role in (MemberRole.STAFF, MemberRole.ADMIN)
        )


class IsOwner(BasePermission):
    """예매/결제/티켓/쿠폰 API의 소유권 검증. 15.2절 '요청자 소유권 검증'."""

    owner_field = "member_id"

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.role == MemberRole.ADMIN:
            return True
        owner_id = getattr(obj, self.owner_field, None)
        return owner_id == request.user.member_id

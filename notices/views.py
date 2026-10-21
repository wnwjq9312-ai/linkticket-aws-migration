from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.views import APIView

from common.mixins import EnvelopeMixin
from common.permissions import IsStaffOrAdmin
from common.response import success_response

from .models import Notice
from .serializers import NoticeSerializer


class NoticeListView(EnvelopeMixin, generics.ListAPIView):
    """GET /api/notices/ — is_published=True만 노출"""

    serializer_class = NoticeSerializer

    def get_queryset(self):
        return Notice.objects.filter(is_published=True).order_by("-published_at")


class NoticeDetailView(EnvelopeMixin, generics.RetrieveAPIView):
    queryset = Notice.objects.filter(is_published=True)
    serializer_class = NoticeSerializer
    lookup_url_kwarg = "notice_id"
    lookup_field = "notice_id"


class StaffNoticeListCreateView(EnvelopeMixin, generics.ListCreateAPIView):
    """GET/POST /api/staff/notices/ — STAFF/ADMIN 공용. GET은 공개 여부와 무관하게
    전체 공지를 관리용으로 조회하고(공개 목록은 NoticeListView가 별도 담당),
    POST는 직원 페이지 '공지 올리기'다."""

    queryset = Notice.objects.all().order_by("-created_at")
    serializer_class = NoticeSerializer
    permission_classes = [IsStaffOrAdmin]

    def perform_create(self, serializer):
        if serializer.validated_data.get("is_published"):
            serializer.save(author=self.request.user, published_at=timezone.now())
        else:
            serializer.save(author=self.request.user)


class StaffNoticeDeleteView(APIView):
    """DELETE /api/staff/notices/{id}/ — 직원 페이지 '공지 삭제'"""

    permission_classes = [IsStaffOrAdmin]

    def get(self, request, notice_id):
        notice = get_object_or_404(Notice, pk=notice_id)
        return success_response(NoticeSerializer(notice).data)

    def patch(self, request, notice_id):
        notice = get_object_or_404(Notice, pk=notice_id)
        serializer = NoticeSerializer(notice, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        extra = {}
        if serializer.validated_data.get('is_published') and not notice.published_at:
            extra['published_at'] = timezone.now()
        serializer.save(**extra)
        return success_response(serializer.data)

    def delete(self, request, notice_id):
        Notice.objects.filter(pk=notice_id).delete()
        return success_response()

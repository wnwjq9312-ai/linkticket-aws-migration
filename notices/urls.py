from django.urls import path

from . import views

urlpatterns = [
    path("notices/", views.NoticeListView.as_view(), name="notice-list"),
    path("notices/<int:notice_id>/", views.NoticeDetailView.as_view(), name="notice-detail"),
    path("staff/notices/", views.StaffNoticeListCreateView.as_view(), name="staff-notice-list-create"),
    path("staff/notices/<int:notice_id>/", views.StaffNoticeDeleteView.as_view(), name="staff-notice-delete"),
]

from django.urls import path

from . import views

urlpatterns = [
    path("performances/", views.PerformanceListView.as_view(), name="performance-list"),
    path("performances/<int:performance_id>/", views.PerformanceDetailView.as_view(), name="performance-detail"),
    path(
        "performances/<int:performance_id>/schedules/",
        views.PerformanceScheduleListView.as_view(),
        name="performance-schedule-list",
    ),
    path("schedules/<int:schedule_id>/seats/", views.ScheduleSeatListView.as_view(), name="schedule-seat-list"),
    path("seats/<int:seat_id>/hold/", views.SeatHoldView.as_view(), name="seat-hold"),
    path("staff/performances/", views.StaffPerformanceCreateView.as_view(), name="staff-performance-create"),
    path(
        "staff/performances/<int:performance_id>/",
        views.StaffPerformanceUpdateView.as_view(),
        name="staff-performance-update",
    ),
    path(
        "staff/performances/<int:performance_id>/schedules/",
        views.StaffPerformanceScheduleCreateView.as_view(),
        name="staff-performance-schedule-create",
    ),
    path(
        "staff/schedules/<int:schedule_id>/seats/",
        views.StaffSeatBulkCreateView.as_view(),
        name="staff-schedule-seat-bulk-create",
    ),
]

from django.urls import path

from . import views

urlpatterns = [
    path("admin/dashboard/overview/", views.AdminDashboardOverviewView.as_view(), name="admin-dashboard-overview"),
    path(
        "admin/dashboard/performances/<int:performance_id>/",
        views.AdminDashboardPerformanceView.as_view(),
        name="admin-dashboard-performance-detail",
    ),
]

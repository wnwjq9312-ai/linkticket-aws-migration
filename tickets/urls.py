from django.urls import path

from . import views

urlpatterns = [
    path("tickets/", views.TicketListView.as_view(), name="ticket-list"),
    path("tickets/<str:ticket_code>/", views.TicketDetailView.as_view(), name="ticket-detail"),
    path("staff/tickets/verify/", views.StaffTicketVerifyView.as_view(), name="staff-ticket-verify"),
    path("admin/tickets/<int:ticket_id>/block/", views.AdminTicketBlockView.as_view(), name="admin-ticket-block"),
]

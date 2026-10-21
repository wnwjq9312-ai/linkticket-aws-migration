from django.urls import path

from . import views

urlpatterns = [
    path("reservations/", views.ReservationCreateView.as_view(), name="reservation-create"),
    path("reservations/mine/", views.ReservationListView.as_view(), name="reservation-list-mine"),
    path("reservations/<int:reservation_id>/", views.ReservationDetailView.as_view(), name="reservation-detail"),
    path(
        "reservations/<int:reservation_id>/cancel/",
        views.ReservationCancelView.as_view(),
        name="reservation-cancel",
    ),
    path("admin/reservations/", views.AdminReservationListView.as_view(), name="admin-reservation-list"),
]

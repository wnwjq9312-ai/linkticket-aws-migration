from django.urls import path

from . import views

urlpatterns = [
    path("events/", views.EventListView.as_view(), name="event-list"),
    path("events/<int:event_id>/participate/", views.EventParticipateView.as_view(), name="event-participate"),
    path("admin/events/", views.AdminEventCreateView.as_view(), name="admin-event-create"),
]

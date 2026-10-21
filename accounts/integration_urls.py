from django.urls import path
from . import integration_views as views

urlpatterns = [
    path('auth/<str:action>/', views.session_view, name='integration-session'),
    path('admin/staff/', views.members, {'section': 'staff'}, name='integration-staff'),
    path('admin/members/', views.members, {'section': 'members'}, name='integration-members'),
    path('admin/members/<int:member_id>/status/', views.members, {'section': 'members'}, name='integration-member-status'),
]

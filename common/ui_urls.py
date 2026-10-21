from django.urls import path
from . import ui_views as v
from . import upload_views

from events import ui_views as ev

app_name = 'ui'
urlpatterns = [
    path('media/<path:name>', upload_views.media_image, name='media-image'),
    path('nft_images/<path:name>', upload_views.nft_image, name='nft-image'),
    path('staff/rewards/', ev.reward_manage, name='reward-manage'),
    path('performance/<str:show_id>/booking-options/', v.booking_options, name='booking-options'),
    path('performance/<str:show_id>/venue/', v.venue_data, name='venue-data'),
    path('dashboard/events/', v.event_manage, name='event-manage'),
    path('nft/<int:collectible_id>/', ev.nft_detail, name='nft-detail'),
    path('nft/<int:collectible_id>/favorite/', ev.nft_favorite, name='nft-favorite'),
    path('staff/nft/', ev.nft_manage, name='nft-manage'),
    path('', v.home, name='home'),
    path('performances/', v.performances, name='performances'),
    path('performance/<str:show_id>/', v.detail, name='detail'),
    path('login/', v.signin, name='login'),
    path('register/', v.signup, name='register'),
    path('register/complete/', v.signup_complete, name='register-complete'),
    path('logout/', v.signout, name='logout'),
    path('mypage/', v.mypage, name='mypage'),
    path('mypage/<str:section>/', v.mypage, name='mypage-section'),
    path('tickets/', v.mypage, {'section': 'tickets'}, name='tickets'),
    path('notices/', v.notices, name='notices'),
    path('notices/<str:notice_id>/', v.notice_detail, name='notice-detail'),
    path('help/<str:section>/', v.help_page, name='help'),
    path('events/', ev.event_list, name='events'),
    path('events/detail/', ev.event_detail, name='event-detail'),
    path('nft/', ev.nft_list, name='nft'),
    path('nft/guide/', v.collected, {'page': 'nft_guide'}, name='nft-guide'),
    path('nft/payment/', v.collected, {'page': 'nft_payment'}, name='nft-payment'),
    path('nft/complete/', v.collected, {'page': 'nft_payment_complete'}, name='nft-complete'),
    path('dashboard/', v.operations, {'page': 'admin'}, name='dashboard'),
    path('staff/', v.operations, {'page': 'staff'}, name='staff'),
]

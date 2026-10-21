from django.urls import path
from .views import RegisterView, LoginView, register_view, login_view, logout_view, CheckUsernameView, CheckEmailView

urlpatterns = [
    # 1. 백엔드 API 주소 (자바스크립트 fetch가 통신하는 곳)
    path('api/register/', RegisterView.as_view(), name='api-register'),
    path('api/login/', LoginView.as_view(), name='api-login'),
    
    # 2. 브라우저에서 직접 들어가는 웹페이지 화면 주소
    path('register/', register_view, name='register-page'),
    path('login/', login_view, name='login-page'),

    # 3. 로그아웃
    path('logout/', logout_view, name='logout'),

    path('api/check-username/', CheckUsernameView.as_view(), name='api-check-username'),
    path('api/check-email/', CheckEmailView.as_view(), name='api-check-email'),
]
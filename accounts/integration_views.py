"""UI adapters for the collected frontend; no schema or legacy API replacement."""
import json

from django.contrib.auth import authenticate, login, logout, get_user_model
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from .serializers import RegisterSerializer


def member_data(user):
    return dict(member_id=user.pk, login_id=user.username, name=user.get_full_name() or user.username,
                email=user.email, phone=user.phone_number or '', role=user.role,
                member_status='ACTIVE' if user.is_active else 'SUSPENDED')


def response(data=None, status=200, message=''):
    return JsonResponse({'success': status < 400, 'data': data, 'message': message}, status=status)


@ensure_csrf_cookie
@require_http_methods(['GET', 'POST'])
def session_view(request, action):
    if action == 'me' and request.method == 'GET':
        return response(member_data(request.user)) if request.user.is_authenticated else response(status=401, message='로그인이 필요합니다.')
    if request.method != 'POST':
        return response(status=405)
    if action == 'logout':
        logout(request)
        return response(message='로그아웃되었습니다.')
    if action != 'login':
        return response(status=404)
    try:
        data = json.loads(request.body)
        if not isinstance(data, dict):
            raise ValueError('Expected JSON object')
    except (ValueError, UnicodeDecodeError):
        return response(status=400, message='입력 형식을 확인해주세요.')
    user = authenticate(request, username=data.get('login_id', data.get('username', '')), password=data.get('password', ''))
    if not user:
        return response(status=400, message='아이디 또는 비밀번호를 확인해주세요.')
    login(request, user)
    return response(member_data(user))


@require_http_methods(['GET', 'POST', 'PATCH'])
def members(request, section, member_id=None):
    if not request.user.is_authenticated or request.user.role != 'ADMIN':
        return response(status=403, message='관리자 권한이 필요합니다.')
    User = get_user_model()
    if request.method == 'GET':
        users = User.objects.order_by('pk')
        if section == 'staff':
            users = users.filter(role='STAFF')
        return response([member_data(user) for user in users])
    try:
        data = json.loads(request.body)
        if not isinstance(data, dict):
            raise ValueError('Expected JSON object')
    except (ValueError, UnicodeDecodeError):
        return response(status=400, message='입력 형식을 확인해주세요.')
    if request.method == 'POST' and section == 'staff':
        serializer = RegisterSerializer(data=dict(username=data.get('login_id'), password=data.get('password'),
             first_name=data.get('name', ''), email=data.get('email', ''), phone_number=data.get('phone', '')))
        if not serializer.is_valid():
            return response(status=400, message=str(serializer.errors))
        user = serializer.save()
        user.role = 'STAFF'
        user.save(update_fields=['role'])
        return response(member_data(user), status=201)
    if request.method == 'PATCH' and member_id:
        user = User.objects.filter(pk=member_id).first()
        if not user:
            return response(status=404)
        if user.is_superuser or user == request.user:
            return response(status=400, message='관리자 계정은 이 화면에서 정지할 수 없습니다.')
        if data.get('member_status') not in ('ACTIVE', 'SUSPENDED'):
            return response(status=400, message='회원 상태를 확인해주세요.')
        user.member_status = data['member_status']
        user.save(update_fields=['member_status'])
        return response(member_data(user))
    return response(status=405)

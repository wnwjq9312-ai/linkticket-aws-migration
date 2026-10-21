from rest_framework import status

from rest_framework.response import Response

from rest_framework.views import APIView

from rest_framework.permissions import AllowAny

from django.contrib.auth import authenticate, login, logout, get_user_model

from django.shortcuts import render, redirect

from .serializers import RegisterSerializer

User = get_user_model()

# 1. 회원가입 API (DRF)

class RegisterView(APIView):

    permission_classes = [AllowAny]
    authentication_classes = [] 


    def post(self, request):

        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():

            serializer.save()

            return Response({"message": "회원가입 완료!"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# 2. 로그인 API (DRF)

# 2. 로그인 API (DRF)
class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [] 

    def post(self, request):
        print("받은 데이터:", request.data)  # 터미널에 데이터 출력
        username = request.data.get('username')
        password = request.data.get('password')
        
        try:
            # 1. DB에서 아이디로 유저를 직접 찾습니다.
            user = User.objects.get(username=username)
            print("찾은 유저:", user)
            
            # 2. 비밀번호가 일치하는지 직접 검증합니다.
            if user.check_password(password):
                login(request, user)  # 세션 생성 (로그인 처리)
                return Response({"message": "로그인 성공!"}, status=status.HTTP_200_OK)
            else:
                print("비밀번호 불일치")
                return Response({"error": "아이디 또는 비밀번호가 잘못되었습니다."}, status=status.HTTP_400_BAD_REQUEST)
                
        except User.DoesNotExist:
            print("존재하지 않는 유저")
            return Response({"error": "아이디 또는 비밀번호가 잘못되었습니다."}, status=status.HTTP_400_BAD_REQUEST)

       

# 3. 회원가입 웹페이지 렌더링

def register_view(request):

    return render(request, 'accounts/register.html')



# 4. 로그인 웹페이지 렌더링 (통합 UI를 쓰므로 동일하게 register.html 연결)

def login_view(request):

    return render(request, 'accounts/register.html')


# 5. 로그아웃
def logout_view(request):
    logout(request)
    return redirect('/')


# 6. 아이디 중복확인
class CheckUsernameView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        username = request.query_params.get('username', '').strip()
        if not username:
            return Response({"available": False, "message": "아이디를 입력해주세요."})
        if User.objects.filter(username=username).exists():
            return Response({"available": False, "message": "이미 사용 중인 아이디입니다."})
        return Response({"available": True, "message": "사용 가능한 아이디입니다."})

# 7. 이메일 중복확인
class CheckEmailView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        email = request.query_params.get('email', '').strip()
        if not email:
            return Response({"available": False, "message": "이메일을 입력해주세요."})
        if User.objects.filter(email__iexact=email).exists():
            return Response({"available": False, "message": "이미 사용 중인 이메일입니다."})
        return Response({"available": True, "message": "사용 가능한 이메일입니다."})
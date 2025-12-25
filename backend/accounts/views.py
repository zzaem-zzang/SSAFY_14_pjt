from django.contrib.auth import authenticate, get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token

from .serializers import UserSerializer, RegisterSerializer

# settings.AUTH_USER_MODEL 에 등록된 User 모델 사용
User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    # 회원가입 요청 데이터를 RegisterSerializer로 검증
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # 유저 생성
    user = serializer.save()

    # 회원가입과 동시에 토큰 발급
    token, _ = Token.objects.get_or_create(user=user)

    # 응답 데이터 구성
    data = UserSerializer(user).data
    data['token'] = token.key

    return Response(data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def login(request):
    # 요청 데이터에서 username, password 추출
    username = request.data.get('username')
    password = request.data.get('password')

    # Django 인증 시스템을 통한 사용자 인증
    user = authenticate(
        request,
        username=username,
        password=password
    )

    # 인증 실패 시
    if not user:
        return Response(
            {'detail': 'invalid credentials'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 로그인 성공 시 토큰 발급 (이미 있으면 재사용)
    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        'token': token.key,
        'user': UserSerializer(user).data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def withdraw(request):
    """
    POST /api/auth/withdraw/
    - 로그인된 사용자 본인 탈퇴
    - User 삭제 시 Token 및 FK 연관 객체 자동 삭제
    """
    user = request.user

    # 사용자 삭제
    user.delete()

    return Response(
        {'detail': '회원탈퇴가 완료되었습니다.'},
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info(request):
    # 로그인된 사용자 본인 정보 반환
    return Response({
        'id': request.user.id,
        'username': request.user.username,
        'nickname': request.user.nickname,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    # 현재 사용자에게 발급된 토큰 삭제
    try:
        request.user.auth_token.delete()
    except:
        # 토큰이 없거나 이미 삭제된 경우 무시
        pass

    return Response(
        {'detail': 'Logged out'},
        status=status.HTTP_200_OK
    )

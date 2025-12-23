from django.contrib.auth import authenticate, get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token

from .serializers import UserSerializer, RegisterSerializer

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = serializer.save()

    # 회원가입과 동시에 토큰 발급 (선택)
    token, _ = Token.objects.get_or_create(user=user)

    data = UserSerializer(user).data
    data['token'] = token.key

    return Response(data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(
        request,
        username=username,
        password=password
    )

    if not user:
        return Response(
            {'detail': 'invalid credentials'},
            status=status.HTTP_400_BAD_REQUEST
        )

    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        'token': token.key,
        'user': UserSerializer(user).data
    })


# 회원탈퇴
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def withdraw(request):
    """
    POST /api/auth/withdraw/
    - 로그인된 사용자 본인 탈퇴
    - 관련 Token 자동 삭제
    """
    user = request.user

    # 사용자 삭제 (Token, Comment, Reaction 등 FK 연쇄 삭제됨)
    user.delete()

    return Response(
        {'detail': '회원탈퇴가 완료되었습니다.'},
        status=status.HTTP_200_OK
    )
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info(request):
    return Response({
        'id': request.user.id,
        'username': request.user.username,
        'nickname': request.user.nickname,
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        request.user.auth_token.delete()
    except:
        pass

    return Response(
        {'detail': 'Logged out'},
        status=status.HTTP_200_OK
    )

# from django.contrib.auth import authenticate, get_user_model
# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.authtoken.models import Token
# from .serializers import UserSerializer

# User = get_user_model()


# class RegisterView(APIView):
#     def post(self, request):
#         username = request.data.get('username')
#         password = request.data.get('password')
#         email = request.data.get('email', '')
#         if not username or not password:
#             return Response({'detail': 'username and password required'}, status=status.HTTP_400_BAD_REQUEST)
#         if User.objects.filter(username=username).exists():
#             return Response({'detail': 'username already exists'}, status=status.HTTP_400_BAD_REQUEST)
#         user = User.objects.create_user(username=username, password=password, email=email)
#         token, _ = Token.objects.get_or_create(user=user)
#         data = UserSerializer(user).data
#         data['token'] = token.key
#         return Response(data, status=status.HTTP_201_CREATED)


# class LoginView(APIView):
#     def post(self, request):
#         username = request.data.get('username')
#         password = request.data.get('password')
#         user = authenticate(request, username=username, password=password)
#         if not user:
#             return Response({'detail': 'invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
#         token, _ = Token.objects.get_or_create(user=user)
#         data = {'token': token.key, 'user': UserSerializer(user).data}
#         return Response(data)


# class LogoutView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         # Delete token to invalidate
#         try:
#             token = Token.objects.get(user=request.user)
#             token.delete()
#         except Token.DoesNotExist:
#             pass
#         return Response({'detail': 'Logged out'}, status=status.HTTP_200_OK)


# class UserView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         return Response(UserSerializer(request.user).data)


from django.contrib.auth import authenticate, get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer

User = get_user_model()
@api_view(['POST'])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')

    if not username or not password:
        return Response(
            {'detail': 'username and password required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {'detail': 'username already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.create_user(
        username=username,
        password=password,
        email=email
    )

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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        token = Token.objects.get(user=request.user)
        token.delete()
    except Token.DoesNotExist:
        pass

    return Response(
        {'detail': 'Logged out'},
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info(request):
    return Response(
        UserSerializer(request.user).data
    )


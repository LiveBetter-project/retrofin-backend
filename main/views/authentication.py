from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from main.serializers import (
    UserSerializer,
    RegisterSerializer,
    LoginSerializer,
    RefreshTokenSerializer,
)

User = get_user_model()


class AuthenticationView(viewsets.ViewSet):

    @action(methods=['post'], detail=False, permission_classes=[AllowAny])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'message': 'User registered successfully',
        }, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=False, permission_classes=[AllowAny])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
        )

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'message': 'Login successful',
            })

        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    @action(methods=['post'], detail=False, permission_classes=[AllowAny])
    def refresh(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = RefreshToken(serializer.validated_data['refresh_token'])
            return Response({
                'token': str(token.access_token),
                'refresh_token': str(token),
                'message': 'Token refreshed successfully',
            })
        except Exception:
            return Response(
                {'error': 'Invalid or expired refresh token'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def logout(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                RefreshToken(refresh_token).blacklist()
        except Exception:
            pass
        return Response({'message': 'Logout successful'})

    @action(methods=['get', 'put', 'patch'], detail=False, permission_classes=[IsAuthenticated])
    def profile(self, request):
        if request.method == 'GET':
            return Response(UserSerializer(request.user).data)

        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=(request.method == 'PATCH'),
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

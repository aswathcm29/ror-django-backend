from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    phonenumber = request.data.get('phonenumber')
    role = request.data.get('role', 'patient')

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=400)

    user = User(username=username, phonenumber=phonenumber, role=role)
    user.set_password(password)
    user.save()

    refresh = RefreshToken.for_user(user)

    return Response({
        'username': user.username,
        'token': str(refresh.access_token),
    }, status=201)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'error': 'Invalid username'}, status=400)

    if user.check_password(password):
        refresh = RefreshToken.for_user(user)
        return Response({
            'username': user.username,
            'token': str(refresh.access_token),
        }, status=200)
    else:
        return Response({'error': 'Invalid password'}, status=401)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request):
    user = request.user
    return Response({
        'username': user.username,
    })

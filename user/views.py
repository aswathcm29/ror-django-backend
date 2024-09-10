import jwt
import datetime
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from .models import User

def generate_token(user):
    payload = {
        'username': user.username,
        'phonenumber': user.phonenumber,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)  # Add expiration
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

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

    token = generate_token(user)

    return Response({
        'username': user.username,
        'phonenumber': user.phonenumber,
        'token': token,
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
        token = generate_token(user)
        return Response({
            'username': user.username,
            'phonenumber': user.phonenumber,
            'token': token,
        }, status=200)
    else:
        return Response({'error': 'Invalid password'}, status=401)

# @api_view(['GET'])
# @permission_classes([AllowAny])  
# def get_user(request):
#     auth_header = request.headers.get('Authorization')
    
#     if not auth_header or not auth_header.startswith('Bearer '):
#         raise AuthenticationFailed('Invalid token header. No token found.')
    
#     token = auth_header.split(' ')[1]
    
#     try:
#         # Decode the token
#         decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        
#         username = decoded_token.get('username')
#         phonenumber = decoded_token.get('phonenumber')
        
#         if not username or not phonenumber:
#             raise AuthenticationFailed('Invalid token. Missing data.')

#         return Response({
#             'username': username,
#             'phonenumber': phonenumber,
#         })
        
#     except jwt.ExpiredSignatureError:
#         raise AuthenticationFailed('Token has expired.')
#     except jwt.InvalidTokenError as e:
#         raise AuthenticationFailed(f'Invalid token: {str(e)}')
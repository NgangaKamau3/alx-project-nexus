from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from apps.users.models import User
from django.conf import settings
import requests

class GoogleLogin(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), settings.GOOGLE_CLIENT_ID)
            email = idinfo.get('email')
            if not email:
                return Response({'error': 'Email not provided by Google'}, status=status.HTTP_400_BAD_REQUEST)
            
            first_name = idinfo.get('given_name', '')
            last_name = idinfo.get('family_name', '')
            picture = idinfo.get('picture', '')
            
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email.split('@')[0],
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_verified': True
                }
            )
            
            if not user.is_verified:
                user.is_verified = True
                user.save()
            
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_verified': user.is_verified
                },
                'created': created
            })
        except ValueError as e:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FacebookLogin(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            response = requests.get(
                f'https://graph.facebook.com/me?fields=id,email,first_name,last_name,picture&access_token={token}',
                timeout=10
            )
            data = response.json()
            
            if 'error' in data:
                return Response({'error': 'Invalid Facebook token'}, status=status.HTTP_400_BAD_REQUEST)
            
            email = data.get('email')
            if not email:
                return Response({'error': 'Email not provided by Facebook'}, status=status.HTTP_400_BAD_REQUEST)
            
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email.split('@')[0],
                    'first_name': data.get('first_name', ''),
                    'last_name': data.get('last_name', ''),
                    'is_verified': True
                }
            )
            
            if not user.is_verified:
                user.is_verified = True
                user.save()
            
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_verified': user.is_verified
                },
                'created': created
            })
        except requests.RequestException:
            return Response({'error': 'Failed to verify Facebook token'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

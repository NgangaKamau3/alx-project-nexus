import logging
import traceback
from django.utils import timezone
from django.conf import settings
from django.middleware.csrf import get_token
from datetime import timedelta

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.core_auth.base_view import BaseAPIView
from apps.users.core_auth.response import standardized_response
from apps.users.auth.services import AuthenticationService

logger = logging.getLogger(__name__)

class UserRegistrationView(BaseAPIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        try:
            email = request.data.get('email')
            password = request.data.get('password')
            phone_number = request.data.get('phone_number')
            full_name = request.data.get('full_name')

        # Use service layer for registration logic
            success, response_data, status_code= AuthenticationService.register(
                email=email,
                password=password,
                phone_number=phone_number,
                full_name=full_name,
                request_meta=request.META
            )

            # Create the response object
            response = Response(
                standardized_response(**response_data),
                status=status_code
            )

        # Set refresh token cookie if registration was successful and cookie security is enabled
            if success and status_code in (200, 201) and settings.JWT_COOKIE_SECURE:
                tokens = response_data.get('data', {}).get('tokens, {}')
                if 'refresh_token' in tokens and 'refresh_token' in tokens:
                    response.set_cookie(
                        key= settings.JWT_COOKIE_NAME,
                        value= tokens['refresh_token'], 
                        expires= timezone.now() + timedelta(seconds=tokens['refresh_expires_in']),
                        secure= True,
                        httponly=True,
                        samesite="Strict",
                        path='/',
                        domain=settings.SESSION_COOKIE_DOMAIN
                    )
            
                if success:
                    get_token(request)
                return response
        except Exception as e:
            logger.error(f"Registration error {str(e)}")
            logger.error(traceback.format_exc())
            return Response(
                standardized_response(success=False, error="Registration failed. Please try again"),
                status=status.HTTP_400_BAD_REQUEST
            )
        

class UserLoginView(BaseAPIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]
    
    def post(self, request):
        try:
            email = request.data.get('email')
            password = request.data.get('password')
            device_info = request.data.get('device_info', {})

            # Use service layer for login
            success, response_data, status_code = AuthenticationService.login(
                email=email,
                password=password,
                device_info=device_info,
                request_meta=request.META
            )

            # Create response object
            response = Response(
                standardized_response(**response_data),
                status=status_code
            )

            # Set refresh token cookie was successful and cookie security is enabled
            if success and status_code == 200 and settings.JWT_COOKIE_SECURE:
                tokens = response_data.get('data', {}).get('tokens', {})
                if 'refresh_token' in tokens and 'refresh_expires_in' in tokens:
                    response.set_cookie(
                        key=settings.JWT_COOKIE_NAME,
                        value= tokens['refresh_token'],
                        expires=timezone.now() + timedelta(seconds=tokens['refresh_expires_in']),
                        secure=True,
                        httponly=True,
                        samesite= "Strict",
                        path='/',
                        domain=settings.SESSION_COOKIE_DOMAIN
                    )

            # Set CSRF token for added security
            if success:
                get_token(request)
            return response
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            logger.error(traceback.format_exc())
            return Response(
                standardized_response(success=False, error="An unexpected error occured. Please try again later."),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class TokenRefreshView(BaseAPIView):
    """
    API endpoint for refreshing JWT tokens with robust security measures. """
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]
    def post(self, request):
        try:
            # First, try to get refresh token from request body. 
            refresh_token = request.data.get('refresh_token')


            # If not in body, try to get from HTTP only cookie
            if not refresh_token and settings.JWT_COOKIE_SECURE:
                refresh_token = request.COOKIES.get(settings.JWT_COOKIE_NAME)
            
            # Use service layer for token refresh logic
            success, response_data, status_code = AuthenticationService.refresh_token(refresh_token)

            # Create response object
            response = Response(
                standardized_response(**response_data),
                status=status_code
            )

            # Update HTTP-only cookie if enabled and refresh was successful
            if success and status_code == 200 and settings.JWT_COOKIE_SECURE:
                tokens = response_data.get('data', {})
                if 'refresh_token' in tokens and 'expires_in' in tokens:
                    response.set_cookie(
                        key=settings.JWT_COOKIE_NAME,
                        value=tokens['refresh_token'],
                        expires=timezone.now() + timedelta(seconds=tokens['expires_in']),
                        secure=True,
                        httponly=True,
                        samesite= "Strict",
                        path='/',
                        domain=settings.SESSION_COOKIE_DOMAIN
                    )
            if success:
                get_token(request)

            return response
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return Response(
                standardized_response(success=False, error="An error occures during token refresh"), status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class ValidateTokenView(BaseAPIView):
    """
    Token validation with additional security checks
    
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Get token from authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

            # Use service layer for token validation logic
            success, response_data, status_code = AuthenticationService.validate_token(token, user)
            return Response(
                standardized_response(**response_data), 
                status=status_code
            )
        
        return Response(
            standardized_response(success=False, error="No token provided."),
            status=status.HTTP_400_BAD_REQUEST
        )

class LogoutView(BaseAPIView):
    """
    Logout endpoint that invalidates tokens
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user

            # Get refresh token
            refresh_token = None

            # Try to get from request data
            if 'refresh_token' in request.data:
                refresh_token = request.data.get('refresh_token')

            # try to get from cookie if enabled
            elif settings.JWT_COOKIE_SECURE:
                refresh_token = request.COOKIES.get(settings.JWT_COOKIE_NAME)
            
            # Use service layer for logout
            success, response_data, status_code = AuthenticationService.logout(user, refresh_token)

            # Create response object
            response = Response(
                standardized_response(**response_data),
                status=status_code
            )

            # Clear refresh token cookie if it was used
            if settings.JWT_COOKIE_SECURE:
                response.delete_cookie(
                    key=settings.JWT_COOKIE_NAME,
                    path='/',
                    domain=settings.SESSION_COOKIE_DOMAIN
                )
            
            return response
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            logger.error(traceback.format_exc())

            # Still try to clear the cookie on error
            response = Response(
                standardized_response(
                    success=True,
                    message="Logout processed"
                ),
                status=status.HTTP_200_OK
            )

            if settings.JWT_COOKIE_SECURE:
                response.delete_cookie(
                    key=settings.JWT_COOKIE_NAME,
                    path='/',
                    domain=settings.SESSION_COOKIE_DOMAIN
                )
            return response

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
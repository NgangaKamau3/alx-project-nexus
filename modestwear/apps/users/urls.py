from django.urls import path, include
from apps.users.auth.views import(UserLoginView, UserRegistrationView, TokenRefreshView, ValidateTokenView, LogoutView)
from apps.users.profile.views import UserProfileView
from apps.users.verification.views import (VerifyEmailView, SendVerificationEmailView, CheckVerificationStatusView, PasswordResetView, ConfirmPasswordResetView)

app_name = 'users'

urlpatterns = [
	path('login/', UserLoginView.as_view(), name='login'),
	path('register/', UserRegistrationView.as_view(), name= 'register'),
	path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
	path('token/validate/', ValidateTokenView.as_view(), name= 'validate-token'),
	path('logout/', LogoutView.as_view(), name= 'logout'),
	
    # Profile routes
	path('profile/', UserProfileView.as_view(), name= 'profile'),
	
    # Verification routes
	path('email-verify/', VerifyEmailView.as_view(), name= 'verify-email'),
	path('send-verification/', SendVerificationEmailView.as_view(), name= 'check-verification'),
	path('verification-status/', CheckVerificationStatusView.as_view(), name='check_verification'),
	path('password-reset/', PasswordResetView.as_view(), name='password-reset'),
	path('password-reset-confirm/', ConfirmPasswordResetView.as_view(), name= 'confirm_password_reset')
]
import logging
import traceback
from django.core.cache import cache
from django.contrib.auth import get_user_model
import threading
from apps.users.core_auth.jwt_utils import TokenManager
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from apps.users.verification.emails import EmailService
from apps.users.verification.tokens import TokenVerifier


logger = logging.getLogger(__name__)
User = get_user_model()
class PasswordResetService:
    """Service class to handle password reset operations."""
    @staticmethod
    def request_reset(email):
        """
        Request password reset for email.
        Args:
            email(str): User email
        Returns:
            tuple: (success, response_dict, status_code)
        """
        try:
            if not email:
                return False, {
                    "success": False,
                    "error": "Email is required"
                }, 400
            # Rate limiting by email to prevent abuse
            rate_key = f"password_reset_{email}"
            if cache.get(rate_key):
                return True, {
                    "success": True,
                    "message": "If an account exists with this email, a password reset link will be sent."
                }, 200
            # find user by email
            try: 
                user = User.objects.get(email=email)

            # send email in background thread
                threading.Thread(
                    target=EmailService.send_password_reset_email,
                    args=(user,),
                    daemon=True
                ).start()
            except User.DoesNotExist:
                pass

        # Rate limit regardless of result(to prevent enumeration attacks)
            cache.set(rate_key, True, timeout=300)

        # For security, return success message regardless of actual result
            return True, {
                "success": True,
                "message": "If an account exists with this email, a password reset link will be sent"
            }, 200
        except Exception as e: 
            logger.error(f"Password reset error: {str(e)}")

            # For security, don't expose error details
            return True, {
                "success": True,
                "message": "If an account exists with this email, a password reset link will be sent."
            }, 200
    @staticmethod
    def confirm_reset(uidb64, token, new_password):
        """
        Complete password reset with token and new password
        
        :param uidb64(str): Base64 encoded ID
        :param token(str): Reset token
        :param new_password(str): New password
        Returns:
            tuple: (success, response_dict, status_code)
        """
        is_valid, user, error = TokenVerifier.verify_token(uidb64, token)
        
        if not is_valid:
            return False, {
                "success": False,
                "error": error or "Invalid password reset link. Please request a new one"
            }, 400
        
        # Validate new password
        try:
            validate_password(new_password, user=user)

        except ValidationError as e:
            return False, {
                "success": False,
                "error": ", ".join(e.messages)
            }
        
        # Update password
        user.set_password(new_password)
        user.save['password']

        # Log password for security audit
        logger.info(f"Password reset completed for user {user.id} via link")

        # Invalidate all existing refresh tokens for security
        TokenManager.blacklist_all_user_tokens(user.id)

        return True, {
            "success": True,
            "message": "Password has been reset successfully. You can now log in with your new password."
        }, 200
    
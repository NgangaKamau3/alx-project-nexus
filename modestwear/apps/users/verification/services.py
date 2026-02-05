import logging
import threading
import traceback
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from apps.users.verification.emails import EmailService
from apps.users.verification.tokens import TokenVerifier


User = get_user_model
logger = logging.getLogger(__name__)

class EmailVerificationService:
    """Service class to handle email verification operations"""

    @staticmethod
    def get_verification_cache_key(user_id):
        """Get standardized cache key for user verification status"""
        return f"user_verification_status_{user_id}"
    
    @staticmethod
    def send_verification_email(user):
        """Send verification email to user
        Args: 
            user: User object
        
        Returns:
            tuple: (success, response_dict, status_code)
        """
        try:
            if user.is_verified:
                return True, {
                    "success": True,
                    "message": "Email already verified"
                }, 200
            

            # Rate limiting per user
            rate_key = f"verification_email_{user.id}"
            if cache.get(rate_key):
                # Get timeout remaining in seconds
                timeout_value = 300
                return False, {
                    "success": False,
                    "error": "Please wait before requesting another verification email",
                    "retry_after": timeout_value
                }, 429
            
            # Queue verification email to be sent in background
            try:
                # Queue verification email to be sent in background
                threading.Thread(
                    target=EmailVerificationService.send_verification_email_background,
                    args= (user.id),
                    daemon=True
                    ).start()
                
                # Set rate limiting regardless of background thread success
                cache.set(rate_key, True, timeout=300)
                logger.info(f"Verification email queued for {user.email}")
                return True, {
                    "success": True,
                    "message": "Verification email sent successfully. Please check your email inbox."
                }, 200
            except Exception as thread_error:
                logger.error(f"Failed to queue verification email thread: {str(thread_error)}")
                return False, {
                    "success": False,
                    "error": "Failed to send verification email. Please try again later."
                }, 500
        except Exception as e: 
            logger.error(f"Send verification email error {str(e)}")
            return False, {
                "success": False,
                "error": "Failed to send verification email. Please try again later."
            }, 400
    
    @staticmethod
    def verify_email(uidb64, token):
        """ 
        Verify email with token.
        Args:
            uidb64(str): Base64 encoded user ID
            token(str): Verification token
        Returns:
            tuple: (success, response_dict, status_code)
        """
        is_valid, user, error = TokenVerifier.verify_token(uidb64, token)

        if not is_valid:
            logger.warning(f"Invalid token verification attempt with uidb64: {uidb64}")
            return False, {
                "success": False,
                "error": error or "Invalid verification link. Please request a new one"
            }, 400
        
        try:
            # Ensure we use an atomic transaction
            from django.db import transaction
            with transaction.atomic():
                # Update user verification status if not already verified
                if not user.is_verified:
                    user.is_verified = True
                    user.save(update_fields=['is_verified'])
                    logger.info(f"Email verified for user {user.id} ({user.email}) via link.")
                else:
                    logger.info(f"Email verification attempt for already verified user: {user.id} ({user.email})")
            # Explicitly clear any related cache entries using our standardized key
            cache_key = EmailVerificationService.get_verification_cache_key(user.id)

            # Set the verified status to True in cache
            cache.set(cache_key, True, timeout=3600)
            logger.info(f"Updated verification cache for user {user.id}: set to True")
            return True, {
                "success": True,
                "message": "Email verification successful."
            }, 200
        except Exception as e:
            logger.error(f"Error during email verification: {str(e)}")
            return False, {
                "success": False,
                "error": "An error occured during verification. Please try again"
            }, 500

    @staticmethod
    def send_verification_email_background(user_id):
        """Background method for sending verification emails.
        Args:
        user_id: User ID
        """
        # forward to email service
        try:
            # Queue verification email with retry
            EmailService.send_verification_email_with_retry(user_id, 3)
            logger.info(f"Background verification email queued for user ID: {user_id}")
        except Exception as e:
            logger.error(f"Failed to send background verification email: {str(e)}")
            logger.error(traceback.format_exc())
    
    @staticmethod
    def check_verification_status(user):
        """
        Check email verification status
        Args:
            user: User object
        Returns:
            tuple: (success, response_dict, status_code)
        """
        try:
            cache_key = EmailVerificationService.get_verification_cache_key(user.pk)
            cached_status = cache.get(cache_key)

            # If we have a cached status, use it
            if cached_status is not None:
                logger.info(f"Using cached verification status for user {user.pk}: {cached_status}")
                return True, {
                    "success": True,
                    "data": {'is_verified': cached_status}
                }, 200
            
            # If not in cache, query the database
            try:
                fresh_user = User.objects.get(pk=user.pk)
                is_verified = fresh_user.is_verified

                # Cache the result for future queries

                cache.set(cache_key, is_verified, timeout=3600)
                logger.info(f"Fetched verification status from DB for user {user.pk}: {is_verified}")
                return True, {
                    "success": True,
                    "data": {'is_verified': is_verified}
                }, 200
            except User.DoesNotExist:
                logger.error(f"User {user.pk} mpt found in database.")
                return False, {
                    "success": False,
                    "error": "User not found"
                }, 404
        except Exception as e:
            logger.error(f"Check verification status error: {str(e)}")

            # Return last known status from DB to degrade gracefully
            return True, {
                "success": True,
                "data": {'is_verified': user.is_verified},
                "message": "Could not check latest status using existing information"
            }, 200
    
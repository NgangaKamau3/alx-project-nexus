import logging
import traceback
import time
import random
import string
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model

User = get_user_model()
logger =  logging.getLogger(__name__)

class EmailService:
    """Service for sending verification emails."""
    @staticmethod
    def send_verification_email(user):
        """Send verification to user with both link and code
        Args:
            user: user object
        Returns:
            bool: Success status
        """
        try:
            # Generate verification token for link
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            # Create verification link
            verify_url = f"{settings.FRONTEND_URL}/auth/email-verify?uid={uid}&token={token}"

            # Compose email
            subject = f"{settings.APP_NAME} - Verify your email address"
            context = {
                'user': user,
                'verify_url': verify_url,
                'app_name': settings.APP_NAME,
                'code_expiry': '1 hour'
            }

            try:
                html_message = render_to_string('emails/verify_email.html', context)
                # Plain text fallback - create a simple text version
                plain_message = f"""Hello {user.email},
                Please verify your email by clicking the link below:
                {verify_url}
                Thank you,
                {settings.APP_NAME} Team
                """
            
            except Exception as template_error:
                logger.error(f"Template rendering error: {str(template_error)}")
                html_message = None
                plain_message = f"""
                Hello {user.email}
                Please verify your email by clicking the link below:

                {verify_url}
                Thank you,
                {settings.APP_NAME} Team.
                """

                # Verify SMTP settings before sending
                try:
                    # Check if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are set
                    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
                        logger.error("Email credentials not configured properly in settings.")
                        return False
                    from_email = settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER
                    send_mail(
                        subject= subject,
                        message=plain_message,
                        from_email=from_email,
                        recipient_list=[user.email],
                        html_message=html_message,
                        fail_silently=False
                    )
                    logger.info(f"Verification email sent to {user.email}")
                    return True
                except Exception as send_error:
                    logger.error(f"SMTP error sending verification email: {str(send_error)}")
                    logger.error(traceback.format_exc())
                    return False
        except Exception as e:
            logger.error(f"Error in verification email preparation: {str(e)}")
            logger.error(traceback.format_exc())
            return False




    @staticmethod
    def send_verification_email_with_retry(user_id, max_attempts=3):
        try:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                logger.error(f"Background verification email: User {user_id} does not exist")
                return
            if user.is_verified:
                logger.info(f"Background verification: User {user.email} already verified")
                return
            # Make multiple attempts with backoff
            for attempt in range(1, max_attempts+1):
                try:
                    success = EmailService.send_verification_email(user)
                    if success:
                        logger.info(f"Background email sent to {user.email} on attempt {attempt}")
                        return
                    else:
                        logger.error(f"Failed to send verification email on attempt {attempt}")

                except Exception as e:
                    logger.error(f"Error in background verification email attempt {attempt}: {str(e)}")

                # Exponential backoff between attempts
                if attempt < max_attempts:
                    time.sleep(2 ** attempt)
            logger.error(f"Failed to send email after {max_attempts} attempts.")
        except Exception as e:
            logger.error(f"Background verification email critical error: {str(e)}")
            logger.error(traceback.format_exc)
        
    @staticmethod
    def send_password_reset_email(user):
        """Send password reset email to user with link
        Args: 
            user(str): User object
        Returns:
            tuple: (bool, reset_code) - success status
        """
        try:
            # Generate verification token for link
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            # Create verification link
            reset_url = f"{settings.FRONTEND_URL}/auth/password-reset-confirm?uid={uid}&token={token}"

            # Compose email
            subject = f"{settings.APP_NAME} - Reset your password"
            context = {
                'user': user,
                'verify_url': reset_url,
                'app_name': settings.APP_NAME,
                'code_expiry': '1 hour'
            }

            try:
                html_message = render_to_string('emails/password_reset.html', context)
                # Plain text fallback - create a simple text version
                plain_message = f"""Hello {user.email},
                You requested to reset your password for your {settings.APP_NAME} account.
                Please click the link below to reset your password:

                {reset_url}
                If you didn't request this please ignore this email. 
                Thank you,
                {settings.APP_NAME} Team
                """
            
            except Exception as template_error:
                logger.error(f"Template rendering error: {str(template_error)}")
                html_message = None
                plain_message = f"""
                Hello {user.email}
                You requested to reset your password for your {settings.APP_NAME} account.
                Please click the link below to reset your password:

                {reset_url}
                If you didn't request this, please ignore this email. 
                Thank you,
                {settings.APP_NAME} Team
                """

                # Verify SMTP settings before sending
            try:
                    # Check if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are set
                if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
                    logger.error("Email credentials not configured properly in settings.")
                    return False
                from_email = settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER
                send_mail(
                    subject= subject,
                    message=plain_message,
                    from_email=from_email,
                    recipient_list=[user.email],
                    html_message=html_message,
                    fail_silently=False
                )
                logger.info(f"Password reset email was sent to {user.email}")
                return True
            except Exception as send_error:
                logger.error(f"Error sending password reset email: {str(send_error)}")
                logger.error(traceback.format_exc())
                return False
        except Exception as e:
            logger.error(f"Error sending password reset email: {str(e)}")
            logger.error(traceback.format_exc())
            return False
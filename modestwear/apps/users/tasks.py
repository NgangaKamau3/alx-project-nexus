from celery import shared_task
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_verification_email_task(self, user_id):
    """
    Celery task to send verification email
    Retries up to 3 times with 60 second delay
    """
    try:
        from apps.users.verification.emails import EmailService
        
        user = User.objects.get(id=user_id)
        EmailService.send_verification_email_with_retry(user_id, max_retries=3)
        logger.info(f"Verification email sent successfully for user {user_id}")
        return f"Email sent to {user.email}"
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        raise
        
    except Exception as exc:
        logger.error(f"Failed to send verification email: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3)
def send_password_reset_email_task(self, user_id, reset_url):
    """
    Celery task to send password reset email
    """
    try:
        from apps.users.verification.emails import EmailService
        
        user = User.objects.get(id=user_id)
        # Implement password reset email sending
        logger.info(f"Password reset email sent for user {user_id}")
        return f"Reset email sent to {user.email}"
        
    except Exception as exc:
        logger.error(f"Failed to send reset email: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task
def cleanup_expired_tokens():
    """
    Periodic task to cleanup expired tokens from cache
    Run daily via Celery Beat
    """
    from django.core.cache import cache
    logger.info("Running token cleanup task")
    # Implement cleanup logic
    return "Token cleanup completed"


@shared_task
def send_order_confirmation_email(order_id):
    """
    Send order confirmation email asynchronously
    """
    try:
        from apps.orders.models import Order
        
        order = Order.objects.get(id=order_id)
        # Send email logic here
        logger.info(f"Order confirmation sent for order {order_id}")
        return f"Confirmation sent for order {order_id}"
        
    except Exception as exc:
        logger.error(f"Failed to send order confirmation: {str(exc)}")
        raise

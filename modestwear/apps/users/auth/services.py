import logging
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from apps.users.serializers import UserSerializer
from apps.users.core_auth.jwt_utils import TokenManager
from apps.users.models import User
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)


class AuthenticationService:
    """Service class to handle authentication-related business logic"""
    @staticmethod
    def register(email, password, phone_number=None, full_name=None, request_meta=None):
        """Handle user registration with email and password. 
        Args:
            email(str): user email
            password(str): User password
            phone_number(str, optional): User's phone number 
            full_name(str, optional): User's full name
            request_meta(dict, optional): Request metadata for security logging
        Returns:
            tuple: (success, response_dict, status_code)
            """
        from apps.users.verification. services import EmailVerificationService
        if not email or not password:
            return False, {"Success": False, "error": "Email and passwword are requires"}, 400
        
        if request_meta:
            logger.info(f"Registration attempt from IP: {request_meta.get('REMOTE_ADDR')}")

        try:
            if User.objects.filter(email=email).exists():
                return False, {
                    "success": False,
                    "error": "A user with this email already exists."
                }, 400
            try:
                validate_password(password)
            except ValidationError as e:
                return False, {
                    "success": False,
                    "error": ", ".join(e.messages)
                }, 400
            user = User.objects.create_user(
                email=email,
                password=password,
                is_verified = False  #Email verification needed


            )

            # Update additional fields if provided
            if full_name:
                user.full_name = full_name
                user.save(update_fields = ['full_name'])

            if phone_number:
                user.phone_number = phone_number
                user.save(update_fields = ['phone_number'])

            # Queue verification email for new users asynchronously
            if user.email and settings.REQUIRE_EMAIL_VERIFICATION:
                # Use cache to mark that verification email should be sent
                cache_key = f"queue_verification_email_{user.id}"
                cache.set(cache_key, True, timeout=3600) # Use one hour queue validity
                
                try:
                # Trigger an asynchronous task for EmailVerificationService for sending emails
                    EmailVerificationService.send_verification_email_background(user.id)
                    logger.info(f"Queued verification email for user: {user.email}")
                except Exception as thread_error:
                    # Log but don't fail registration if email queuing fails
                    logger.error(f"Failed to queue verification email {str(thread_error)}")
                
        # Serialize user data
            serializer = UserSerializer(user)

        # Generate tokens
            tokens = TokenManager.generate_tokens(user)

        # Log successful registration

            logger.info(f"Regsitration successful for user: {user.email}")

        # return successful response data
            return True, {
                "success": True,
                "data": {
                    "user" : serializer.data,
                    "tokens": tokens,
                    "is_new_user": True,
                    "email_verified": user.is_verified
                }
            }, 201
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return False,  {
                "success": False,
                "error": "Registration failed. Please try again."
            }, 400
        
    @staticmethod
    def login(email, password, device_info=None, request_meta=None):
        """
        Handle user login with email and password
        Args:
            email(str): User email
            password(str): User password
            device_info(dict, optional): Device info for audit
            request_meta(dict, optionsl): Request metadata for security logging
            
        Retuns:
            tuple: (success, response_dict, status_code)
            """
        if not email or not password:
            return False, {
                "success": False,
                "error": "Email and password are required"
            }, 400
        
        # Log login attempt with security metadata
        if request_meta:
            logger.info(f"Login attempt from IP: {request_meta.get('REMOTE_ADDR')} User-Agent: {request_meta.get('HTTP_USER_AGENT')}")

        try:
            # Check for account lockout
            if cache.get(f"account_lockout {email}"):
                logger.warning(f"Login attempt for locked account: {email}")
                return False, {
                    "success": False,
                    "error": "Acccount temporarily locked due to multiple failed attempts. Try again later.",
                    "lockout": True
                }, 403
            
            # Authenticate with Django's system
            user = authenticate(username=email, password=password)

            # If authentication fails
            if not user:
                # Increment failed login attempts
                failed_attempts = cache.get(f"failed_logins: {email}", 0), +1
                cache.set(f"failed_logins: {email}", failed_attempts, timeout=1800)
                if failed_attempts >= 5:
                     cache.set(f"account_lockout: {email}", True, timeout=900)
                     logger.warning(f"Account locked due to failed attempts: {email}")
                     return False, {
                        "success": False,
                        "error": "Account temporarily locked due to multiple attempts. Try again later.",
                        "lockout": True
                     }, 403
                logger.warning(f"Failed login attempt for email: {email}")
                return False, {
                    "success": False,
                    "error": "Invalid email or password",
                }, 401
            
            if not user.is_active:
                logger.warning(f"Login attempt for disabled account: {email}")
                return False, {
                    "success": False,
                    "error": "Account is disabled. Please contact support."
                }, 403
                
                cache.delete(f"failed_logins: {email}")
                serializer = UserSerializer(user)

                # Generate tokens
                tokens = TokenManager.generate_tokens(user)

                # Record login with devide info for audit trail
                user.last_login = timezone.now()
                user.save(update_fields=['last_login'])

                # Log successful login

                if request_meta:
                    logger.info(f"Login successful for user: {user.email} from IP: {request_meta.get('REMOTE_ADDR')}")

                # Return successful response
                return True, {
                    "data": {
                        "user": serialzer.data,
                        "tokens": tokens,
                        "email_verified": user.is_verified,
                        "verification_needed": not user.is_verified and settings.REQUIRE_EMAIL_VERIFICATION
                    }
                }, 200
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return False, {
                "success": False,
                "error": "Authentication failed. Please try again"
            }, 401
                
                

                


    




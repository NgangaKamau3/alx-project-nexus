from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
import jwt
import logging
import uuid
import time
from django.utils import timezone

logger = logging.getLogger(__name__)

class TokenManager:
    """Enhanced JWT token manager with security features"""
    @staticmethod
    def generate_tokens(user):
        """Generate secure access and refresh tokens with enhanced claims and security."""
        try:
            refresh = RefreshToken.for_user(user)
            
            #  Create JTI
            jti = str(uuid.uuid4())
            
            # Add custom claims with security considerations
            refresh['jti'] = jti
            refresh['username'] = user.username
            refresh['is_staff'] = user.is_verified
            refresh['email'] = user.email
            refresh['type'] = 'refresh'
            
            access_token = refresh.access_token
            access_token['type'] = 'access'
            access_token['jti'] = str(uuid.uuid4)

            # Get expiration times from settings
            access_expiry = settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFEIME', timedelta(minutes=15))
            refresh_expiry = settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME', timedelta(days=14))

            # Store token metadata in cache for potential revocation
            TokenManager._store_token_metadata(user.id, jti, refresh_expiry.total_seconds())

            return {
                'access_token': str(access_token),
                'refresh_token': str(refresh),
                'expires_in': int(access_expiry.total_seconds()),
                'user_id': user.id,
                'issued_at': int(time.time())
            }
        except Exception as e:
            logger.error(f"Failed to generate tokens for user {user.id}: {str(e)}")
    @staticmethod
    def refresh_tokens(refresh_token):
        """Refresh token with validation and optional rotation"""
        try:
            token = RefreshToken(refresh_token)

            # Check if token is blacklisted
            jti = token.get(jti)
            if not jti or TokenManager.is_token_blacklisted(jti):
                logger.warning(f"Attempt to use blacklisted token with JTI: {jti}")
                raise TokenError("Token is blacklisted")
            
            # Get user from token
            user_id = token.get('user_id')
            from apps.users.models import User
            # Import here to avoid circular imports
            try:
                user = User.objects.get(id=user_id)
            except:
                logger.warning(f"Token refresh attempted for non-existent user id: {user_id}")
                raise TokenError("Invalid Token")
            if not user.is_active:
                logger.warning(f"Token refresh attempted for inactive user: {user.email}")
                raise TokenError("User is inactive.")
            
            # If current rotation is enabled, blacklist the current token

            if settings.SIMPLE_JWT.get("ROTATE_REFRESH_TOKENS", True):
                TokenManager.blacklist_token(jti)

            return TokenManager.generate_tokens(user)
        except TokenError as e:
            logger.warning(f"Token refresh error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected errpr during token refresh: {str(e)}")
            raise TokenError(f"Token refresh failed: {str(e)}")
            
    @staticmethod
    def validate_token(token_string):
        """Validate token without using the DB.
        Returns tuple (is_valid. user_id, token_type)"""
        try:
            # First use PyJWT to decode without verification to get the algorithm
            unverified = jwt.decode(token_string, options={"verify_signature": False})
            alg = unverified.get('alg', settings.SIMPLE_JWT.get('ALGORITHM', 'HS256'))

            # Properly decode and verify
            decoded = jwt.decode(token_string, settings.SIMPLE_JWT('SIGNING_KEY', settings.SECRET_KEY), algorithms=[alg], options= {"verify_signature": True})
            # Check token type
            token_type =  decoded.get('token_type', decoded.get('type', 'access'))
            user_id = decoded.get('user_id')
            jti = decoded.get('jti')

            # Check if token is blacklisted
            if jti and TokenManager.is_token_blacklisted(jti):
                logger.warning(f"Attemot to use blacklisted token with jti: {jti}")
                return False, None, None
            exp = decoded.get('exp', 0)
            if exp < time.time():
                logger.debug(f"Token expired at {datetime.fromtimestamp(exp).isoformat()}")
                return False, None, None
            return True, user_id, token_type
        except jwt.PyJWTError as e:
            logger.debug(f"Token validation error: {str(e)}")
            return False, None, None
            

    @staticmethod
    def _store_token_metadata(user_id, jti, expiry_seconds):
        """Store token metadata in cache for blacklisting."""

        try:
            if hasattr(cache, 'client'):
            # Redis implementation
                user_tokens_key = f"user_tokens: {user_id}"
                pipe = cache.client.pipeline()
                pipe.sadd(user_tokens_key, jti)
                pipe.expire(user_tokens_key, int(expiry_seconds))
            else:
                # Generic implementation for LocMemCache
                user_tokens_key = f"user_tokens: {user_id}"
                token_set = cache.get(user_tokens_key, set())
                if not isinstance(token_set, set):
                        token_set = set()
                token_set.add(jti)
                cache.set(user_tokens_key, token_set, timeout=int(expiry_seconds))
        except Exception as e:
            logger.error(f"Error storing token metadata: {str(e)}")
    @staticmethod
    def blacklist_token(jti):
        """Blacklist a token by JTI"""
        if not jti:
            return False
        # Add to blacklist with expiry

        blacklist_key = f"blacklisted_token: {jti}"
        cache.set(blacklist_key, True, timeout=settings.SIMPLE_JWT.get('BLACKLIST_TIMEOUT', 86400))
    @staticmethod
    def is_token_blacklisted(jti):
        """Check if a token is blacklisted"""
        if not jti:
            return False
        blacklist_key = f"blacklisted_token: {jti}"
        return cache.get(blacklist_key)
    
    @staticmethod
    def blacklist_all_user_tokens(user_id):
        """Blacklist all tokens for a specific user."""
        try:
            user_tokens_key = f"user_tokens: {user_id}"
            if hasattr(cache, 'client'):
                active_tokens = cache.client.smembers(user_tokens_key)
                if not active_tokens:
                    return 0 
                
                for jti in active_tokens:
                    TokenManager.blacklist_token(jti.decode('utf-8') if isinstance(jti, bytes) else jti)
                
                cache.delete(user_tokens_key)
                return len(active_tokens)
            else:
                token_set = cache.get(user_tokens_key, set())
                if not token_set:
                    return 0
                for jti in token_set:
                    TokenManager.blacklist_token(jti)

                cache.delete(user_tokens_key)
                return len(token_set)
        except Exception as e:
            logger.error(f"Error blacklisting user tokens: {str(e)}")
            return 0
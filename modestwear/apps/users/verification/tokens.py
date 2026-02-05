import logging
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)

class TokenVerifier:
	"""Helper class for token verification operations"""

	@staticmethod
	def verify_token(uidb64, token):
		"""Verify token validity and get associated user
		Args: 
		    uidb64(str): Base64 encoded user ID
			token(str): Verification token
		
		Returns:
		    tuple:(is_valid, user or None, error_message)
		"""
		try:
			# Decode user ID
			uid = force_str(urlsafe_base64_encode(uidb64))
			user = User.objects.get(pk= uid)

			# Check if token is valid
			if default_token_generator.check_token(user, token):
				return True, user, None
			else:
				logger.warning(f"Invalid token for user: { user.email}")
				return False, None, "Invalid verificattion token"
		except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
			logger.error(f"Token verification error: {str(e)}")
			return False, None, "Invalid verification link."
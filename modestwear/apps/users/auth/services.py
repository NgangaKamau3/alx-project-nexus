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

			)
		
		except:
			pass
import pytest
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch, Mock
from apps.users.auth.services import AuthService
from apps.users.profile.services import ProfileService
from apps.users.verification.services import EmailVerificationService
from apps.users.serializers import UserRegistrationSerializer, UserProfileSerializer

User = get_user_model()

@pytest.mark.django_db
class UserModelTests(TestCase):
    def test_user_creation(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)
    
    def test_superuser_creation(self):
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
    
    def test_user_str_method(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(str(user), 'testuser')

@pytest.mark.django_db
class AuthViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_registration(self):
        url = reverse('users:register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_user_registration_password_mismatch(self):
        url = reverse('users:register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password_confirm': 'differentpass',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_login(self):
        url = reverse('users:login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_user_login_invalid_credentials(self):
        url = reverse('users:login')
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_token_refresh(self):
        refresh = RefreshToken.for_user(self.user)
        url = reverse('users:token-refresh')
        data = {'refresh': str(refresh)}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_user_logout(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.force_authenticate(user=self.user)
        url = reverse('users:logout')
        data = {'refresh': str(refresh)}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

@pytest.mark.django_db
class ProfileViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_get_profile_authenticated(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('users:profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_get_profile_unauthenticated(self):
        url = reverse('users:profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_update_profile(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('users:profile')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')

@pytest.mark.django_db
class EmailVerificationViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_active=False
        )
    
    @patch('apps.users.verification.services.EmailVerificationService.send_verification_email')
    def test_send_verification_email(self, mock_send_email):
        mock_send_email.return_value = True
        url = reverse('users:send-verification')
        data = {'email': 'test@example.com'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_send_email.assert_called_once()
    
    @patch('apps.users.verification.services.EmailVerificationService.verify_email')
    def test_verify_email(self, mock_verify):
        mock_verify.return_value = True
        url = reverse('users:verify-email')
        data = {'token': 'test-token'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class UserRegistrationSerializerTests(TestCase):
    def test_valid_registration_data(self):
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_password_mismatch(self):
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'differentpass',
            'first_name': 'Test',
            'last_name': 'User'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password_confirm', serializer.errors)
    
    def test_duplicate_username(self):
        User.objects.create_user(
            username='testuser',
            email='existing@example.com',
            password='testpass123'
        )
        data = {
            'username': 'testuser',  # Duplicate username
            'email': 'new@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())

class UserProfileSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_profile_serializer(self):
        serializer = UserProfileSerializer(self.user)
        self.assertEqual(serializer.data['username'], 'testuser')
        self.assertEqual(serializer.data['email'], 'test@example.com')
        self.assertNotIn('password', serializer.data)

@pytest.mark.django_db
class AuthServiceTests(TestCase):
    def setUp(self):
        self.service = AuthService()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_authenticate_user_valid_credentials(self):
        user = self.service.authenticate_user('testuser', 'testpass123')
        self.assertEqual(user, self.user)
    
    def test_authenticate_user_invalid_credentials(self):
        user = self.service.authenticate_user('testuser', 'wrongpassword')
        self.assertIsNone(user)
    
    def test_create_user_tokens(self):
        tokens = self.service.create_user_tokens(self.user)
        self.assertIn('access', tokens)
        self.assertIn('refresh', tokens)
        self.assertIsInstance(tokens['access'], str)
        self.assertIsInstance(tokens['refresh'], str)
    
    def test_register_user(self):
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        user = self.service.register_user(user_data)
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertTrue(user.check_password('newpass123'))

@pytest.mark.django_db
class ProfileServiceTests(TestCase):
    def setUp(self):
        self.service = ProfileService()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_update_profile(self):
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com'
        }
        updated_user = self.service.update_profile(self.user, update_data)
        self.assertEqual(updated_user.first_name, 'Updated')
        self.assertEqual(updated_user.last_name, 'Name')
        self.assertEqual(updated_user.email, 'updated@example.com')
    
    def test_get_user_profile(self):
        profile_data = self.service.get_user_profile(self.user)
        self.assertEqual(profile_data['username'], 'testuser')
        self.assertEqual(profile_data['email'], 'test@example.com')
        self.assertEqual(profile_data['first_name'], 'Test')

@pytest.mark.django_db
class EmailVerificationServiceTests(TestCase):
    def setUp(self):
        self.service = EmailVerificationService()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_active=False
        )
    
    def test_generate_verification_token(self):
        token = self.service.generate_verification_token(self.user)
        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 0)
    
    def test_verify_token_valid(self):
        token = self.service.generate_verification_token(self.user)
        is_valid = self.service.verify_token(token, self.user)
        self.assertTrue(is_valid)
    
    def test_verify_token_invalid(self):
        is_valid = self.service.verify_token('invalid-token', self.user)
        self.assertFalse(is_valid)
    
    @patch('apps.users.verification.emails.send_verification_email')
    def test_send_verification_email(self, mock_send_email):
        mock_send_email.return_value = True
        result = self.service.send_verification_email(self.user)
        self.assertTrue(result)
        mock_send_email.assert_called_once()

@pytest.mark.django_db
class PasswordResetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @patch('apps.users.verification.password_reset_service.PasswordResetService.send_reset_email')
    def test_request_password_reset(self, mock_send_email):
        mock_send_email.return_value = True
        url = reverse('users:password-reset-request')
        data = {'email': 'test@example.com'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_send_email.assert_called_once()
    
    @patch('apps.users.verification.password_reset_service.PasswordResetService.reset_password')
    def test_reset_password(self, mock_reset):
        mock_reset.return_value = True
        url = reverse('users:password-reset-confirm')
        data = {
            'token': 'test-token',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
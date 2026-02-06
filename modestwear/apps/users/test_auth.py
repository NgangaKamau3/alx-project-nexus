import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from django.urls import reverse

User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.mark.auth
class TestUserRegistration:
    """Test user registration endpoint"""
    
    def test_register_user_success(self, api_client):
        """Test successful user registration"""
        url = reverse('users:register')
        data = {
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'username': 'newuser',
            'phone_number': '+1234567890'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        assert 'tokens' in response.data['data']
        assert 'user' in response.data['data']
        assert response.data['data']['user']['email'] == data['email']
        assert User.objects.filter(email=data['email']).exists()
    
    def test_register_duplicate_email(self, api_client, user):
        """Test registration with existing email"""
        url = reverse('users:register')
        data = {
            'email': user.email,
            'password': 'SecurePass123!',
            'username': 'anotheruser'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False
    
    def test_register_weak_password(self, api_client):
        """Test registration with weak password"""
        url = reverse('users:register')
        data = {
            'email': 'newuser@example.com',
            'password': '123',
            'username': 'newuser'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False
    
    def test_register_missing_fields(self, api_client):
        """Test registration with missing required fields"""
        url = reverse('users:register')
        data = {'email': 'newuser@example.com'}
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.auth
class TestUserLogin:
    """Test user login endpoint"""
    
    def test_login_success(self, api_client, user):
        """Test successful login"""
        url = reverse('users:login')
        data = {
            'email': 'test@example.com',
            'password': 'TestPass123!'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'tokens' in response.data['data']
        assert 'access_token' in response.data['data']['tokens']
        assert 'refresh_token' in response.data['data']['tokens']
    
    def test_login_invalid_credentials(self, api_client, user):
        """Test login with invalid credentials"""
        url = reverse('users:login')
        data = {
            'email': 'test@example.com',
            'password': 'WrongPassword'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['success'] is False
    
    def test_login_nonexistent_user(self, api_client):
        """Test login with non-existent user"""
        url = reverse('users:login')
        data = {
            'email': 'nonexistent@example.com',
            'password': 'TestPass123!'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_missing_fields(self, api_client):
        """Test login with missing fields"""
        url = reverse('users:login')
        data = {'email': 'test@example.com'}
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.auth
class TestTokenRefresh:
    """Test token refresh endpoint"""
    
    def test_refresh_token_success(self, api_client, user_tokens):
        """Test successful token refresh"""
        url = reverse('users:token_refresh')
        data = {'refresh_token': user_tokens['refresh']}
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access_token' in response.data['data']
        assert 'refresh_token' in response.data['data']
    
    def test_refresh_invalid_token(self, api_client):
        """Test refresh with invalid token"""
        url = reverse('users:token_refresh')
        data = {'refresh_token': 'invalid_token'}
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.auth
class TestUserProfile:
    """Test user profile endpoints"""
    
    def test_get_profile_authenticated(self, authenticated_client, user):
        """Test getting profile when authenticated"""
        url = reverse('users:profile')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['email'] == user.email
        assert response.data['data']['username'] == user.username
    
    def test_get_profile_unauthenticated(self, api_client):
        """Test getting profile without authentication"""
        url = reverse('users:profile')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_profile(self, authenticated_client, user):
        """Test updating user profile"""
        url = reverse('users:profile')
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'phone_number': '+9876543210'
        }
        response = authenticated_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['first_name'] == 'John'
        assert response.data['data']['last_name'] == 'Doe'
        
        user.refresh_from_db()
        assert user.first_name == 'John'


@pytest.mark.auth
class TestLogout:
    """Test logout endpoint"""
    
    def test_logout_success(self, authenticated_client, user_tokens):
        """Test successful logout"""
        url = reverse('users:logout')
        data = {'refresh_token': user_tokens['refresh']}
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
    
    def test_logout_unauthenticated(self, api_client):
        """Test logout without authentication"""
        url = reverse('users:logout')
        response = api_client.post(url, {}, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

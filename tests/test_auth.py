"""
API tests for authentication endpoints
"""
import pytest
from django.contrib.auth.models import User
from rest_framework import status


@pytest.mark.django_db
class TestAuthRegistration:
    """Test user registration endpoint"""
    
    def test_register_success(self, api_client):
        """Test successful user registration"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'New',
            'last_name': 'User',
            'is_creator': False
        }
        response = api_client.post('/api/auth/register/', data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'token' in response.data
        assert 'user' in response.data
        assert response.data['user']['username'] == 'newuser'
        assert User.objects.filter(username='newuser').exists()
        assert User.objects.get(username='newuser').profile is not None
    
    def test_register_as_creator(self, api_client):
        """Test registering as a creator"""
        data = {
            'username': 'newcreator',
            'email': 'creator@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'is_creator': True,
            'bio': 'This is a long enough bio for validation'
        }
        response = api_client.post('/api/auth/register/', data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['user']['is_creator'] is True
        assert User.objects.get(username='newcreator').profile.is_creator is True
    
    def test_register_password_mismatch(self, api_client):
        """Test registration with mismatched passwords"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'password_confirm': 'differentpass',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = api_client.post('/api/auth/register/', data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data or 'non_field_errors' in response.data
    
    def test_register_missing_fields(self, api_client):
        """Test registration with missing required fields"""
        data = {
            'username': 'newuser'
        }
        response = api_client.post('/api/auth/register/', data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_duplicate_username(self, api_client, user):
        """Test registration with duplicate username"""
        data = {
            'username': 'testuser',  # Already exists
            'email': 'different@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        response = api_client.post('/api/auth/register/', data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'username' in response.data
    
    def test_register_weak_password(self, api_client):
        """Test registration with weak password"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': '123',  # Too short
            'password_confirm': '123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = api_client.post('/api/auth/register/', data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestAuthLogin:
    """Test user login endpoint"""
    
    def test_login_success(self, api_client, user):
        """Test successful login"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = api_client.post('/api/auth/login/', data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'token' in response.data
        assert 'user' in response.data
        assert response.data['user']['username'] == 'testuser'
    
    def test_login_invalid_credentials(self, api_client, user):
        """Test login with invalid credentials"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = api_client.post('/api/auth/login/', data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'error' in response.data
    
    def test_login_nonexistent_user(self, api_client):
        """Test login with non-existent user"""
        data = {
            'username': 'nonexistent',
            'password': 'testpass123'
        }
        response = api_client.post('/api/auth/login/', data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_missing_fields(self, api_client):
        """Test login with missing fields"""
        data = {
            'username': 'testuser'
        }
        response = api_client.post('/api/auth/login/', data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


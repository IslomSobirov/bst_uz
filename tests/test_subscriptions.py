"""
API tests for subscription endpoints
"""
import pytest
from rest_framework import status
from rest_framework.authtoken.models import Token

from boosty_app.models import Subscription


@pytest.mark.django_db
class TestSubscriptionList:
    """Test subscription listing"""

    def test_list_subscriptions_authenticated(self, authenticated_client, subscription, user, creator):
        """Test listing subscriptions when authenticated"""
        response = authenticated_client.get('/api/subscriptions/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1

    def test_list_subscriptions_unauthenticated(self, api_client):
        """Test listing subscriptions without authentication"""
        response = api_client.get('/api/subscriptions/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestSubscriptionCreate:
    """Test subscription creation"""

    def test_create_subscription(self, authenticated_client, user, creator):
        """Test creating a subscription"""
        data = {
            'creator_id': creator.profile.id
        }
        response = authenticated_client.post('/api/subscriptions/', data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert user.following.filter(creator=creator.profile).exists()

    def test_create_duplicate_subscription(self, authenticated_client, user, creator, subscription):
        """Test creating duplicate subscription"""
        data = {
            'creator_id': creator.profile.id
        }
        response = authenticated_client.post('/api/subscriptions/', data, format='json')

        # Should return 400 Bad Request with validation error
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'creator_id' in response.data

    def test_create_subscription_unauthenticated(self, api_client, creator):
        """Test creating subscription without authentication"""
        data = {
            'creator_id': creator.profile.id
        }
        response = api_client.post('/api/subscriptions/', data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_subscription_missing_fields(self, authenticated_client):
        """Test creating subscription with missing fields"""
        response = authenticated_client.post('/api/subscriptions/', {}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_subscription_nonexistent_creator(self, authenticated_client):
        """Test creating subscription to non-existent creator"""
        data = {
            'creator_id': 9999
        }
        response = authenticated_client.post('/api/subscriptions/', data, format='json')

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestSubscriptionDelete:
    """Test subscription deletion"""

    def test_delete_subscription(self, authenticated_client, subscription, user, creator):
        """Test deleting a subscription"""
        subscription_id = subscription.id
        response = authenticated_client.delete(f'/api/subscriptions/{subscription_id}/')

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Subscription.objects.filter(id=subscription_id).exists()

    def test_delete_other_user_subscription(self, authenticated_client, subscription, creator):
        """Test deleting someone else's subscription (should fail)"""
        # Create another user and try to delete subscription that doesn't belong to them
        from django.contrib.auth.models import User
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        token = Token.objects.create(user=other_user)
        authenticated_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        response = authenticated_client.delete(f'/api/subscriptions/{subscription.id}/')

        assert response.status_code == status.HTTP_404_NOT_FOUND

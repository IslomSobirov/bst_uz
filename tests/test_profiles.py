"""
API tests for user profile endpoints
"""
import pytest
from rest_framework import status


@pytest.mark.django_db
class TestProfileList:
    """Test profile listing"""

    def test_list_profiles_unauthenticated(self, api_client, user, creator):
        """Test listing profiles without authentication"""
        response = api_client.get('/api/profiles/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 2

    def test_list_profiles_authenticated(self, authenticated_client, user, creator):
        """Test listing profiles with authentication"""
        response = authenticated_client.get('/api/profiles/')

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestProfileDetail:
    """Test profile detail endpoint"""

    def test_get_profile_detail(self, api_client, creator):
        """Test getting a specific profile"""
        profile_id = creator.profile.id
        response = api_client.get(f'/api/profiles/{profile_id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'creator'
        assert response.data['is_creator'] is True

    def test_get_nonexistent_profile(self, api_client):
        """Test getting non-existent profile"""
        response = api_client.get('/api/profiles/9999/')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_own_profile(self, authenticated_client, user):
        """Test updating own profile"""
        profile_id = user.profile.id
        data = {
            'bio': 'Updated bio that is long enough to pass validation'
        }
        response = authenticated_client.patch(f'/api/profiles/{profile_id}/', data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['bio'] == data['bio']

    def test_update_other_profile(self, authenticated_client, creator):
        """Test updating someone else's profile (should fail)"""
        profile_id = creator.profile.id
        data = {'bio': 'Unauthorized update'}
        response = authenticated_client.patch(f'/api/profiles/{profile_id}/', data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestProfileMe:
    """Test /profiles/me/ endpoint"""

    def test_get_own_profile(self, authenticated_client, user):
        """Test getting own profile via /me/ endpoint"""
        response = authenticated_client.get('/api/profiles/me/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'testuser'

    def test_get_me_unauthenticated(self, api_client):
        """Test /me/ endpoint without authentication"""
        response = api_client.get('/api/profiles/me/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestCreatorsList:
    """Test /profiles/creators/ endpoint"""

    def test_list_creators_unauthenticated(self, api_client, creator, multiple_creators):
        """Test listing creators without authentication"""
        response = api_client.get('/api/profiles/creators/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 4  # creator + 3 from multiple_creators
        assert all(profile['is_creator'] for profile in response.data)

    def test_list_creators_authenticated(self, authenticated_client, creator):
        """Test listing creators with authentication"""
        response = authenticated_client.get('/api/profiles/creators/')

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestProfileSubscribe:
    """Test subscription functionality"""

    def test_subscribe_to_creator(self, authenticated_client, user, creator):
        """Test subscribing to a creator"""
        profile_id = creator.profile.id
        response = authenticated_client.post(f'/api/profiles/{profile_id}/subscribe/')

        assert response.status_code == status.HTTP_200_OK
        assert user.following.filter(creator=creator.profile).exists()

    def test_subscribe_already_subscribed(self, authenticated_client, user, creator, subscription):
        """Test subscribing when already subscribed"""
        profile_id = creator.profile.id
        response = authenticated_client.post(f'/api/profiles/{profile_id}/subscribe/')

        assert response.status_code == status.HTTP_200_OK
        assert 'Already subscribed' in response.data.get('status', '')

    def test_subscribe_to_self(self, creator_client, creator):
        """Test subscribing to yourself (should fail)"""
        profile_id = creator.profile.id
        response = creator_client.post(f'/api/profiles/{profile_id}/subscribe/')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_subscribe_unauthenticated(self, api_client, creator):
        """Test subscribing without authentication"""
        profile_id = creator.profile.id
        response = api_client.post(f'/api/profiles/{profile_id}/subscribe/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestProfileUnsubscribe:
    """Test unsubscribe functionality"""

    def test_unsubscribe_from_creator(self, authenticated_client, user, creator, subscription):
        """Test unsubscribing from a creator"""
        profile_id = creator.profile.id
        response = authenticated_client.delete(f'/api/profiles/{profile_id}/unsubscribe/')

        assert response.status_code == status.HTTP_200_OK
        assert not user.following.filter(creator=creator.profile).exists()

    def test_unsubscribe_not_subscribed(self, authenticated_client, user, creator):
        """Test unsubscribing when not subscribed"""
        profile_id = creator.profile.id
        response = authenticated_client.delete(f'/api/profiles/{profile_id}/unsubscribe/')

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestFollowingList:
    """Test /profiles/following/ endpoint"""

    def test_get_following(self, authenticated_client, user, creator, subscription):
        """Test getting list of creators user follows"""
        response = authenticated_client.get('/api/profiles/following/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['username'] == 'creator'

    def test_get_following_no_subscriptions(self, authenticated_client, user):
        """Test getting following when user has no subscriptions"""
        response = authenticated_client.get('/api/profiles/following/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_get_following_unauthenticated(self, api_client):
        """Test getting following without authentication"""
        response = api_client.get('/api/profiles/following/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

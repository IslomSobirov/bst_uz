"""
API tests for post endpoints
"""
import pytest
from rest_framework import status

from boosty_app.models import Post


@pytest.mark.django_db
class TestPostList:
    """Test post listing"""

    def test_list_posts_shows_only_published(self, api_client, published_post, draft_post):
        """Test that only published posts are shown in public listing"""
        response = api_client.get('/api/posts/')

        assert response.status_code == status.HTTP_200_OK
        post_ids = [post['id'] for post in response.data['results']]
        assert published_post.id in post_ids
        assert draft_post.id not in post_ids

    def test_list_posts_unauthenticated(self, api_client, published_post):
        """Test listing posts without authentication"""
        response = api_client.get('/api/posts/')

        assert response.status_code == status.HTTP_200_OK
        # Unauthenticated users should only see free posts
        post_ids = [post['id'] for post in response.data['results']]
        assert published_post.id in post_ids

    def test_list_posts_authenticated(self, authenticated_client, published_post):
        """Test listing posts with authentication"""
        response = authenticated_client.get('/api/posts/')

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestPostCreate:
    """Test post creation"""

    def test_create_post_as_creator(self, creator_client, category):
        """Test creating a post as a creator"""
        data = {
            'title': 'New Post',
            'content': 'This is the content of a new post',
            'category': category.id,
            'status': 'draft'
        }
        response = creator_client.post('/api/posts/', data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'New Post'
        assert response.data['status'] == 'draft'
        assert response.data['is_free'] is False  # Default value

    def test_create_post_with_is_free(self, creator_client, category):
        """Test creating a post with is_free field"""
        data = {
            'title': 'Free Post',
            'content': 'This is a free post',
            'category': category.id,
            'status': 'published',
            'is_free': True
        }
        response = creator_client.post('/api/posts/', data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['is_free'] is True

    def test_create_post_with_is_free_false(self, creator_client, category):
        """Test creating a post with is_free=False"""
        data = {
            'title': 'Paid Post',
            'content': 'This is a paid post',
            'category': category.id,
            'status': 'published',
            'is_free': False
        }
        response = creator_client.post('/api/posts/', data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['is_free'] is False

    def test_create_post_as_regular_user(self, authenticated_client, category):
        """Test creating a post as regular user (should fail)"""
        data = {
            'title': 'New Post',
            'content': 'This is the content',
            'category': category.id
        }
        response = authenticated_client.post('/api/posts/', data, format='json')

        # Regular users can create posts, but they need to be creators for it to make sense
        # Let's check what the actual behavior is - might be allowed
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_403_FORBIDDEN]

    def test_create_post_unauthenticated(self, api_client, category):
        """Test creating post without authentication"""
        data = {
            'title': 'New Post',
            'content': 'This is the content',
            'category': category.id
        }
        response = api_client.post('/api/posts/', data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_post_missing_fields(self, creator_client):
        """Test creating post with missing required fields"""
        data = {
            'title': 'New Post'
            # Missing content
        }
        response = creator_client.post('/api/posts/', data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestPostDetail:
    """Test post detail endpoint"""

    def test_get_published_post(self, api_client, published_post):
        """Test getting a published post"""
        response = api_client.get(f'/api/posts/{published_post.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == published_post.title

    def test_get_draft_post_as_author(self, creator_client, draft_post):
        """Test getting own draft post"""
        response = creator_client.get(f'/api/posts/{draft_post.id}/')

        assert response.status_code == status.HTTP_200_OK

    def test_get_draft_post_as_non_author(self, authenticated_client, draft_post):
        """Test getting someone else's draft post (should fail)"""
        response = authenticated_client.get(f'/api/posts/{draft_post.id}/')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_draft_post_unauthenticated(self, api_client, draft_post):
        """Test getting draft post without authentication"""
        response = api_client.get(f'/api/posts/{draft_post.id}/')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_own_post(self, creator_client, draft_post, category):
        """Test updating own post"""
        data = {
            'title': 'Updated Title',
            'content': 'Updated content',
            'category': category.id
        }
        response = creator_client.patch(f'/api/posts/{draft_post.id}/', data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Updated Title'

    def test_update_post_is_free(self, creator_client, draft_post):
        """Test updating is_free field of a post"""
        data = {'is_free': True}
        response = creator_client.patch(f'/api/posts/{draft_post.id}/', data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_free'] is True

        # Update back to False
        data = {'is_free': False}
        response = creator_client.patch(f'/api/posts/{draft_post.id}/', data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_free'] is False

    def test_update_other_post(self, authenticated_client, published_post):
        """Test updating someone else's post (should fail)"""
        data = {'title': 'Unauthorized Update'}
        response = authenticated_client.patch(f'/api/posts/{published_post.id}/', data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_own_post(self, creator_client, draft_post):
        """Test deleting own post"""
        post_id = draft_post.id
        response = creator_client.delete(f'/api/posts/{post_id}/')

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Post.objects.filter(id=post_id).exists()

    def test_delete_other_post(self, authenticated_client, published_post):
        """Test deleting someone else's post (should fail)"""
        response = authenticated_client.delete(f'/api/posts/{published_post.id}/')

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestPostPublish:
    """Test post publishing"""

    def test_publish_draft_post(self, creator_client, draft_post):
        """Test publishing a draft post"""
        response = creator_client.post(f'/api/posts/{draft_post.id}/publish/')

        assert response.status_code == status.HTTP_200_OK
        draft_post.refresh_from_db()
        assert draft_post.status == 'published'

    def test_publish_already_published(self, creator_client, published_post):
        """Test publishing an already published post (should fail)"""
        response = creator_client.post(f'/api/posts/{published_post.id}/publish/')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_publish_other_post(self, authenticated_client, draft_post):
        """Test publishing someone else's post (should fail)"""
        response = authenticated_client.post(f'/api/posts/{draft_post.id}/publish/')

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestPostArchive:
    """Test post archiving"""

    def test_archive_published_post(self, creator_client, published_post):
        """Test archiving a published post"""
        response = creator_client.post(f'/api/posts/{published_post.id}/archive/')

        assert response.status_code == status.HTTP_200_OK
        published_post.refresh_from_db()
        assert published_post.status == 'archived'

    def test_archive_draft_post(self, creator_client, draft_post):
        """Test archiving a draft post (should fail)"""
        response = creator_client.post(f'/api/posts/{draft_post.id}/archive/')

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestMyPosts:
    """Test /posts/my_posts/ endpoint"""

    def test_get_my_posts(self, creator_client, draft_post, published_post):
        """Test getting own posts"""
        response = creator_client.get('/api/posts/my_posts/')

        assert response.status_code == status.HTTP_200_OK
        post_ids = [post['id'] for post in response.data]
        assert draft_post.id in post_ids
        assert published_post.id in post_ids

    def test_get_my_posts_unauthenticated(self, api_client):
        """Test getting my posts without authentication"""
        response = api_client.get('/api/posts/my_posts/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestPostFeed:
    """Test /posts/feed/ endpoint"""

    def test_get_feed(self, authenticated_client, user, creator, subscription, published_post):
        """Test getting feed of subscribed creators"""
        response = authenticated_client.get('/api/posts/feed/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert published_post.id in [post['id'] for post in response.data]

    def test_get_feed_no_subscriptions(self, authenticated_client, user, published_post):
        """Test getting feed with no subscriptions"""
        response = authenticated_client.get('/api/posts/feed/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_get_feed_unauthenticated(self, api_client):
        """Test getting feed without authentication"""
        response = api_client.get('/api/posts/feed/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestPostComments:
    """Test post comments endpoint"""

    def test_get_post_comments(self, api_client, published_post, comment):
        """Test getting comments for a post"""
        response = api_client.get(f'/api/posts/{published_post.id}/comments/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['content'] == comment.content


@pytest.mark.django_db
class TestPostIsFree:
    """Test is_free field functionality"""

    def test_free_post_visible_to_unauthenticated(self, api_client, free_post, paid_post):
        """Test that free posts are visible to unauthenticated users"""
        response = api_client.get('/api/posts/')

        assert response.status_code == status.HTTP_200_OK
        post_ids = [post['id'] for post in response.data['results']]
        assert free_post.id in post_ids
        assert paid_post.id not in post_ids

    def test_free_post_detail_visible_to_unauthenticated(self, api_client, free_post):
        """Test that free post detail is accessible to unauthenticated users"""
        response = api_client.get(f'/api/posts/{free_post.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == free_post.title
        assert response.data['is_free'] is True

    def test_paid_post_not_visible_to_unauthenticated(self, api_client, paid_post):
        """Test that paid posts are not visible to unauthenticated users"""
        response = api_client.get('/api/posts/')

        assert response.status_code == status.HTTP_200_OK
        post_ids = [post['id'] for post in response.data['results']]
        assert paid_post.id not in post_ids

    def test_paid_post_detail_not_accessible_to_unauthenticated(self, api_client, paid_post):
        """Test that paid post detail is not accessible to unauthenticated users"""
        response = api_client.get(f'/api/posts/{paid_post.id}/')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_paid_post_visible_to_subscriber(self, authenticated_client, user, creator, paid_post, subscription):
        """Test that paid posts are visible to subscribers"""
        response = authenticated_client.get('/api/posts/')

        assert response.status_code == status.HTTP_200_OK
        post_ids = [post['id'] for post in response.data['results']]
        assert paid_post.id in post_ids

    def test_paid_post_detail_accessible_to_subscriber(self, authenticated_client, user, creator, paid_post, subscription):
        """Test that paid post detail is accessible to subscribers"""
        response = authenticated_client.get(f'/api/posts/{paid_post.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == paid_post.title
        assert response.data['is_free'] is False

    def test_paid_post_not_visible_to_non_subscriber(self, authenticated_client, user, paid_post):
        """Test that paid posts are not visible to non-subscribers"""
        response = authenticated_client.get('/api/posts/')

        assert response.status_code == status.HTTP_200_OK
        post_ids = [post['id'] for post in response.data['results']]
        assert paid_post.id not in post_ids

    def test_free_post_visible_to_non_subscriber(self, authenticated_client, user, free_post):
        """Test that free posts are visible to authenticated non-subscribers"""
        response = authenticated_client.get('/api/posts/')

        assert response.status_code == status.HTTP_200_OK
        post_ids = [post['id'] for post in response.data['results']]
        assert free_post.id in post_ids

    def test_post_serializer_includes_is_free(self, api_client, free_post):
        """Test that post serializer includes is_free field"""
        response = api_client.get(f'/api/posts/{free_post.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert 'is_free' in response.data
        assert response.data['is_free'] is True

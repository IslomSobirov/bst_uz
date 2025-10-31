"""
API tests for comment endpoints
"""
import pytest
from rest_framework import status


@pytest.mark.django_db
class TestCommentCreate:
    """Test comment creation"""

    def test_create_comment_authenticated(self, authenticated_client, published_post, user):
        """Test creating a comment when authenticated"""
        data = {
            'post': published_post.id,
            'content': 'This is a new comment'
        }
        response = authenticated_client.post('/api/comments/', data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['content'] == 'This is a new comment'
        assert response.data['author']['username'] == user.username

    def test_create_comment_unauthenticated_on_free_post(self, api_client, free_post):
        """Test creating comment without authentication on free post (should require auth)"""
        data = {
            'post': free_post.id,
            'content': 'This is a comment'
        }
        response = api_client.post('/api/comments/', data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_comment_missing_fields(self, authenticated_client, published_post):
        """Test creating comment with missing fields"""
        data = {
            'post': published_post.id
            # Missing content
        }
        response = authenticated_client.post('/api/comments/', data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_comment_nonexistent_post(self, authenticated_client):
        """Test creating comment on non-existent post"""
        data = {
            'post': 9999,
            'content': 'This is a comment'
        }
        response = authenticated_client.post('/api/comments/', data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_comment_on_paid_post_as_subscriber(self, authenticated_client, user, creator, paid_post, subscription):
        """Test creating comment on paid post when subscribed"""
        data = {
            'post': paid_post.id,
            'content': 'This is a comment on paid post'
        }
        response = authenticated_client.post('/api/comments/', data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['content'] == 'This is a comment on paid post'

    def test_create_comment_on_paid_post_as_non_subscriber(self, authenticated_client, user, paid_post):
        """Test creating comment on paid post when not subscribed (should fail)"""
        data = {
            'post': paid_post.id,
            'content': 'This is a comment'
        }
        response = authenticated_client.post('/api/comments/', data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCommentList:
    """Test comment listing"""

    def test_list_comments(self, api_client, comment, published_post):
        """Test listing comments (only comments on visible posts)"""
        # published_post is free, so comment should be visible
        response = api_client.get('/api/comments/')

        assert response.status_code == status.HTTP_200_OK
        # Should see comments on free posts
        comment_ids = [c['id'] for c in response.data['results']]
        assert comment.id in comment_ids

    def test_list_comments_excludes_paid_post_comments_unauthenticated(self, api_client, creator, paid_post):
        """Test that comments on paid posts are not visible to unauthenticated users"""
        from boosty_app.models import Comment
        comment = Comment.objects.create(
            post=paid_post,
            author=creator,
            content='Comment on paid post'
        )

        response = api_client.get('/api/comments/')

        assert response.status_code == status.HTTP_200_OK
        comment_ids = [c['id'] for c in response.data['results']]
        assert comment.id not in comment_ids

    def test_list_comments_includes_paid_post_comments_for_subscriber(self, authenticated_client, user, creator, paid_post, subscription):
        """Test that comments on paid posts are visible to subscribers"""
        from boosty_app.models import Comment
        comment = Comment.objects.create(
            post=paid_post,
            author=creator,
            content='Comment on paid post'
        )

        response = authenticated_client.get('/api/comments/')

        assert response.status_code == status.HTTP_200_OK
        comment_ids = [c['id'] for c in response.data['results']]
        assert comment.id in comment_ids


@pytest.mark.django_db
class TestCommentDetail:
    """Test comment detail endpoint"""

    def test_get_comment_detail(self, api_client, comment, published_post):
        """Test getting a specific comment on free post"""
        # published_post is free, so comment should be visible
        response = api_client.get(f'/api/comments/{comment.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['content'] == comment.content

    def test_get_comment_on_paid_post_unauthenticated(self, api_client, creator, paid_post):
        """Test getting comment on paid post when unauthenticated (should fail)"""
        from boosty_app.models import Comment
        comment = Comment.objects.create(
            post=paid_post,
            author=creator,
            content='Comment on paid post'
        )

        response = api_client.get(f'/api/comments/{comment.id}/')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_comment_on_paid_post_as_subscriber(self, authenticated_client, user, creator, paid_post, subscription):
        """Test getting comment on paid post when subscribed"""
        from boosty_app.models import Comment
        comment = Comment.objects.create(
            post=paid_post,
            author=creator,
            content='Comment on paid post'
        )

        response = authenticated_client.get(f'/api/comments/{comment.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['content'] == 'Comment on paid post'

    def test_get_comment_on_paid_post_as_non_subscriber(self, authenticated_client, user, creator, paid_post):
        """Test getting comment on paid post when not subscribed (should fail)"""
        from boosty_app.models import Comment
        comment = Comment.objects.create(
            post=paid_post,
            author=creator,
            content='Comment on paid post'
        )

        response = authenticated_client.get(f'/api/comments/{comment.id}/')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_nonexistent_comment(self, api_client):
        """Test getting non-existent comment"""
        response = api_client.get('/api/comments/9999/')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_own_comment(self, authenticated_client, comment, user, published_post):
        """Test updating own comment"""
        # Make sure comment belongs to user
        # published_post is free, so comment should be accessible
        comment.author = user
        comment.save()

        data = {
            'content': 'Updated comment content'
        }
        response = authenticated_client.patch(f'/api/comments/{comment.id}/', data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['content'] == 'Updated comment content'

    def test_update_other_comment(self, authenticated_client, comment, creator, published_post):
        """Test updating someone else's comment (should fail)"""
        # Make sure comment belongs to creator, not the authenticated user
        # published_post is free, so comment should be visible but not editable
        comment.author = creator
        comment.save()

        data = {
            'content': 'Unauthorized update'
        }
        response = authenticated_client.patch(f'/api/comments/{comment.id}/', data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_own_comment(self, authenticated_client, published_post, user):
        """Test deleting own comment"""
        from boosty_app.models import Comment
        comment = Comment.objects.create(
            post=published_post,
            author=user,
            content='Comment to delete'
        )
        comment_id = comment.id

        response = authenticated_client.delete(f'/api/comments/{comment_id}/')

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Comment.objects.filter(id=comment_id).exists()

    def test_delete_other_comment(self, authenticated_client, comment, creator, published_post):
        """Test deleting someone else's comment (should fail)"""
        # Make sure comment belongs to creator, not the authenticated user
        # published_post is free, so comment should be visible but not deletable by others
        comment.author = creator
        comment.save()

        response = authenticated_client.delete(f'/api/comments/{comment.id}/')

        assert response.status_code == status.HTTP_403_FORBIDDEN

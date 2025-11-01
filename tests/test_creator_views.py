"""
Tests for creator dashboard views
"""
import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from boosty_app.models import Category, Comment, Post, Subscription, UserProfile


@pytest.fixture
def django_client():
    """Django test client for template-based views"""
    return Client()


@pytest.fixture
def creator_client(django_client, creator):
    """Authenticated Django client as creator"""
    django_client.force_login(creator)
    return django_client


@pytest.fixture
def regular_user_client(django_client, user):
    """Authenticated Django client as regular user"""
    django_client.force_login(user)
    return django_client


@pytest.mark.django_db
class TestCreatorDashboard:
    """Test creator dashboard view"""

    def test_dashboard_unauthenticated(self, django_client):
        """Test accessing dashboard without authentication"""
        response = django_client.get('/creator/')
        # Should redirect to login
        assert response.status_code in [302, 403]

    def test_dashboard_as_regular_user(self, regular_user_client):
        """Test accessing dashboard as non-creator user"""
        response = regular_user_client.get('/creator/')
        assert response.status_code == 403

    def test_dashboard_as_creator(self, creator_client, creator, category):
        """Test accessing dashboard as creator"""
        # Create some posts for statistics
        Post.objects.create(
            title='Published Post',
            content='Content',
            author=creator,
            category=category,
            status='published'
        )
        Post.objects.create(
            title='Draft Post',
            content='Content',
            author=creator,
            category=category,
            status='draft'
        )

        response = creator_client.get('/creator/')
        assert response.status_code == 200
        assert 'total_posts' in response.context
        assert response.context['total_posts'] == 2
        assert response.context['published_posts'] == 1
        assert response.context['draft_posts'] == 1

    def test_dashboard_shows_recent_posts(self, creator_client, creator, category):
        """Test dashboard displays recent posts"""
        Post.objects.create(
            title='Recent Post',
            content='Content',
            author=creator,
            category=category,
            status='published'
        )

        response = creator_client.get('/creator/')
        assert response.status_code == 200
        assert len(response.context['recent_posts']) >= 1


@pytest.mark.django_db
class TestCreatorPostsList:
    """Test posts list view"""

    def test_posts_list_unauthenticated(self, django_client):
        """Test accessing posts list without authentication"""
        response = django_client.get('/creator/posts/')
        assert response.status_code in [302, 403]

    def test_posts_list_as_regular_user(self, regular_user_client):
        """Test accessing posts list as non-creator"""
        response = regular_user_client.get('/creator/posts/')
        assert response.status_code == 403

    def test_posts_list_as_creator(self, creator_client, creator, category):
        """Test accessing posts list as creator"""
        Post.objects.create(
            title='Post 1',
            content='Content 1',
            author=creator,
            category=category,
            status='published'
        )
        Post.objects.create(
            title='Post 2',
            content='Content 2',
            author=creator,
            category=category,
            status='draft'
        )

        response = creator_client.get('/creator/posts/')
        assert response.status_code == 200
        assert len(response.context['posts']) == 2

    def test_posts_list_with_status_filter(self, creator_client, creator, category):
        """Test posts list with status filter"""
        Post.objects.create(
            title='Published',
            content='Content',
            author=creator,
            category=category,
            status='published'
        )
        Post.objects.create(
            title='Draft',
            content='Content',
            author=creator,
            category=category,
            status='draft'
        )

        response = creator_client.get('/creator/posts/?status=published')
        assert response.status_code == 200
        assert len(response.context['posts']) == 1
        assert response.context['posts'][0].status == 'published'

    def test_posts_list_only_shows_own_posts(self, creator_client, creator, user, category):
        """Test posts list only shows creator's own posts"""
        # Create post by creator
        Post.objects.create(
            title='My Post',
            content='Content',
            author=creator,
            category=category,
            status='published'
        )
        # Create post by another user
        Post.objects.create(
            title='Other Post',
            content='Content',
            author=user,
            category=category,
            status='published'
        )

        response = creator_client.get('/creator/posts/')
        assert response.status_code == 200
        assert len(response.context['posts']) == 1
        assert response.context['posts'][0].title == 'My Post'


@pytest.mark.django_db
class TestCreatePost:
    """Test create post view"""

    def test_create_post_get(self, creator_client):
        """Test GET request to create post form"""
        response = creator_client.get('/creator/posts/create/')
        assert response.status_code == 200
        assert 'form' in response.context

    def test_create_post_unauthenticated(self, django_client):
        """Test creating post without authentication"""
        response = django_client.get('/creator/posts/create/')
        assert response.status_code in [302, 403]

    def test_create_post_as_regular_user(self, regular_user_client):
        """Test creating post as non-creator"""
        response = regular_user_client.get('/creator/posts/create/')
        assert response.status_code == 403

    def test_create_post_post(self, creator_client, creator, category):
        """Test POST request to create post"""
        data = {
            'title': 'New Post',
            'content': 'This is the content',
            'category': category.id,
            'status': 'draft'
        }
        response = creator_client.post('/creator/posts/create/', data)

        assert response.status_code == 302  # Redirect after creation
        post = Post.objects.get(title='New Post')
        assert post.title == 'New Post'
        assert post.author == creator

    def test_create_post_invalid_data(self, creator_client, category):
        """Test creating post with invalid data"""
        data = {
            'title': '',  # Missing title
            'content': 'Content',
            'category': category.id
        }
        response = creator_client.post('/creator/posts/create/', data)

        assert response.status_code == 200  # Form errors, no redirect
        assert 'form' in response.context
        assert not Post.objects.filter(content='Content').exists()


@pytest.mark.django_db
class TestViewPost:
    """Test view post detail"""

    def test_view_post_unauthenticated(self, django_client, creator, category):
        """Test viewing post without authentication"""
        post = Post.objects.create(
            title='Test Post',
            content='Content',
            author=creator,
            category=category,
            status='published'
        )
        response = django_client.get(f'/creator/posts/{post.id}/')
        assert response.status_code in [302, 403]

    def test_view_own_post(self, creator_client, creator, category):
        """Test viewing own post"""
        post = Post.objects.create(
            title='My Post',
            content='Content',
            author=creator,
            category=category,
            status='published'
        )
        response = creator_client.get(f'/creator/posts/{post.id}/')
        assert response.status_code == 200
        assert response.context['post'].id == post.id

    def test_view_other_creator_post(self, creator_client, creator, category, user):
        """Test viewing another creator's post (should fail)"""
        other_creator = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='testpass123'
        )
        other_creator.profile.is_creator = True
        other_creator.profile.save()

        post = Post.objects.create(
            title='Other Post',
            content='Content',
            author=other_creator,
            category=category,
            status='published'
        )
        response = creator_client.get(f'/creator/posts/{post.id}/')
        assert response.status_code == 404

    def test_view_post_with_comments(self, creator_client, creator, category, user):
        """Test viewing post with comments"""
        post = Post.objects.create(
            title='Post with Comments',
            content='Content',
            author=creator,
            category=category,
            status='published'
        )
        Comment.objects.create(
            post=post,
            author=user,
            content='A comment'
        )

        response = creator_client.get(f'/creator/posts/{post.id}/')
        assert response.status_code == 200
        assert len(response.context['comments']) == 1


@pytest.mark.django_db
class TestEditPost:
    """Test edit post view"""

    def test_edit_post_get(self, creator_client, creator, category):
        """Test GET request to edit post form"""
        post = Post.objects.create(
            title='Original Title',
            content='Content',
            author=creator,
            category=category,
            status='draft'
        )
        response = creator_client.get(f'/creator/posts/{post.id}/edit/')
        assert response.status_code == 200
        assert response.context['post'].id == post.id
        assert 'form' in response.context

    def test_edit_post_unauthenticated(self, django_client, creator, category):
        """Test editing post without authentication"""
        post = Post.objects.create(
            title='Post',
            content='Content',
            author=creator,
            category=category,
            status='draft'
        )
        response = django_client.get(f'/creator/posts/{post.id}/edit/')
        assert response.status_code in [302, 403]

    def test_edit_own_post(self, creator_client, creator, category):
        """Test editing own post"""
        post = Post.objects.create(
            title='Original',
            content='Content',
            author=creator,
            category=category,
            status='draft'
        )
        data = {
            'title': 'Updated Title',
            'content': 'Updated content',
            'category': category.id,
            'status': 'published'
        }
        response = creator_client.post(f'/creator/posts/{post.id}/edit/', data)

        assert response.status_code == 302  # Redirect after update
        post.refresh_from_db()
        assert post.title == 'Updated Title'
        assert post.status == 'published'

    def test_edit_other_creator_post(self, creator_client, creator, category):
        """Test editing another creator's post (should fail)"""
        other_creator = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='testpass123'
        )
        other_creator.profile.is_creator = True
        other_creator.profile.save()

        post = Post.objects.create(
            title='Other Post',
            content='Content',
            author=other_creator,
            category=category,
            status='draft'
        )
        response = creator_client.get(f'/creator/posts/{post.id}/edit/')
        assert response.status_code == 404


@pytest.mark.django_db
class TestDeletePost:
    """Test delete post view"""

    def test_delete_post_unauthenticated(self, django_client, creator, category):
        """Test deleting post without authentication"""
        post = Post.objects.create(
            title='Post',
            content='Content',
            author=creator,
            category=category,
            status='draft'
        )
        response = django_client.post(f'/creator/posts/{post.id}/delete/')
        assert response.status_code in [302, 403]
        assert Post.objects.filter(id=post.id).exists()  # Still exists

    def test_delete_own_post(self, creator_client, creator, category):
        """Test deleting own post"""
        post = Post.objects.create(
            title='Post to Delete',
            content='Content',
            author=creator,
            category=category,
            status='draft'
        )
        post_id = post.id
        response = creator_client.post(f'/creator/posts/{post_id}/delete/')

        assert response.status_code == 302  # Redirect after delete
        assert not Post.objects.filter(id=post_id).exists()

    def test_delete_other_creator_post(self, creator_client, creator, category):
        """Test deleting another creator's post (should fail)"""
        other_creator = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='testpass123'
        )
        other_creator.profile.is_creator = True
        other_creator.profile.save()

        post = Post.objects.create(
            title='Other Post',
            content='Content',
            author=other_creator,
            category=category,
            status='draft'
        )
        response = creator_client.post(f'/creator/posts/{post.id}/delete/')
        assert response.status_code == 404
        assert Post.objects.filter(id=post.id).exists()  # Still exists

    def test_delete_post_get_method(self, creator_client, creator, category):
        """Test that GET method is not allowed for delete"""
        post = Post.objects.create(
            title='Post',
            content='Content',
            author=creator,
            category=category,
            status='draft'
        )
        response = creator_client.get(f'/creator/posts/{post.id}/delete/')
        assert response.status_code == 405  # Method not allowed


@pytest.mark.django_db
class TestCreatorComments:
    """Test creator comments view"""

    def test_comments_unauthenticated(self, django_client):
        """Test accessing comments without authentication"""
        response = django_client.get('/creator/comments/')
        assert response.status_code in [302, 403]

    def test_comments_as_creator(self, creator_client, creator, category, user):
        """Test accessing comments as creator"""
        post = Post.objects.create(
            title='Post',
            content='Content',
            author=creator,
            category=category,
            status='published'
        )
        Comment.objects.create(
            post=post,
            author=user,
            content='A comment'
        )

        response = creator_client.get('/creator/comments/')
        assert response.status_code == 200
        assert len(response.context['comments']) == 1

    def test_comments_filter_by_post(self, creator_client, creator, category, user):
        """Test filtering comments by post"""
        post1 = Post.objects.create(
            title='Post 1',
            content='Content',
            author=creator,
            category=category,
            status='published'
        )
        post2 = Post.objects.create(
            title='Post 2',
            content='Content',
            author=creator,
            category=category,
            status='published'
        )
        Comment.objects.create(post=post1, author=user, content='Comment 1')
        Comment.objects.create(post=post2, author=user, content='Comment 2')

        response = creator_client.get(f'/creator/comments/?post={post1.id}')
        assert response.status_code == 200
        assert len(response.context['comments']) == 1
        assert response.context['comments'][0].post.id == post1.id


@pytest.mark.django_db
class TestCreatorSubscribers:
    """Test creator subscribers view"""

    def test_subscribers_unauthenticated(self, django_client):
        """Test accessing subscribers without authentication"""
        response = django_client.get('/creator/subscribers/')
        assert response.status_code in [302, 403]

    def test_subscribers_as_creator(self, creator_client, creator, user):
        """Test accessing subscribers as creator"""
        Subscription.objects.create(
            subscriber=user,
            creator=creator.profile
        )

        response = creator_client.get('/creator/subscribers/')
        assert response.status_code == 200
        assert len(response.context['subscriptions']) == 1
        assert response.context['subscriber_count'] == 1

    def test_subscribers_empty_list(self, creator_client):
        """Test subscribers view with no subscribers"""
        response = creator_client.get('/creator/subscribers/')
        assert response.status_code == 200
        assert len(response.context['subscriptions']) == 0
        assert response.context['subscriber_count'] == 0

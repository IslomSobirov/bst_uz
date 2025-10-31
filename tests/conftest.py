"""
Pytest configuration and fixtures for API tests
"""
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from boosty_app.models import UserProfile, Category, Post, Comment, Subscription


@pytest.fixture
def api_client():
    """API client for making requests"""
    return APIClient()


@pytest.fixture
def user(db):
    """Create a regular user"""
    user = User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )
    return user


@pytest.fixture
def creator(db):
    """Create a creator user"""
    user = User.objects.create_user(
        username='creator',
        email='creator@example.com',
        password='testpass123',
        first_name='Creator',
        last_name='User'
    )
    user.profile.is_creator = True
    user.profile.bio = 'This is a test creator bio that is long enough'
    user.profile.save()
    return user


@pytest.fixture
def authenticated_client(api_client, user):
    """API client authenticated as regular user"""
    token = Token.objects.create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return api_client


@pytest.fixture
def creator_client(api_client, creator):
    """API client authenticated as creator"""
    token = Token.objects.create(user=creator)
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return api_client


@pytest.fixture
def category(db):
    """Create a test category"""
    return Category.objects.create(
        name='Technology',
        description='Technology related posts'
    )


@pytest.fixture
def published_post(db, creator, category):
    """Create a published post"""
    return Post.objects.create(
        title='Test Published Post',
        content='This is the content of a published post',
        author=creator,
        category=category,
        status='published'
    )


@pytest.fixture
def draft_post(db, creator, category):
    """Create a draft post"""
    return Post.objects.create(
        title='Test Draft Post',
        content='This is the content of a draft post',
        author=creator,
        category=category,
        status='draft'
    )


@pytest.fixture
def comment(db, published_post, user):
    """Create a test comment"""
    return Comment.objects.create(
        post=published_post,
        author=user,
        content='This is a test comment'
    )


@pytest.fixture
def subscription(db, user, creator):
    """Create a subscription"""
    return Subscription.objects.create(
        subscriber=user,
        creator=creator.profile
    )


@pytest.fixture
def multiple_creators(db):
    """Create multiple creator users"""
    creators = []
    for i in range(3):
        user = User.objects.create_user(
            username=f'creator{i}',
            email=f'creator{i}@example.com',
            password='testpass123'
        )
        user.profile.is_creator = True
        user.profile.bio = f'Creator {i} bio that is long enough to pass validation'
        user.profile.save()
        creators.append(user)
    return creators


@pytest.fixture
def multiple_posts(db, creator, category):
    """Create multiple published posts"""
    posts = []
    for i in range(5):
        post = Post.objects.create(
            title=f'Published Post {i}',
            content=f'Content of post {i}',
            author=creator,
            category=category,
            status='published'
        )
        posts.append(post)
    return posts


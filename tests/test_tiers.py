"""Comprehensive tests for subscription tier functionality"""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone

from boosty_app.models import Post, SubscriptionTier, TierSubscription, UserProfile


@pytest.mark.django_db
class TestSubscriptionTierModel:
    """Test SubscriptionTier model"""

    def test_create_tier(self, creator_user):
        """Test creating a subscription tier"""
        tier = SubscriptionTier.objects.create(
            creator=creator_user.profile,
            name="Basic",
            description="Basic tier with access to exclusive content",
            price=Decimal('5.00'),
            order=0,
            is_active=True
        )

        assert tier.name == "Basic"
        assert tier.price == Decimal('5.00')
        assert tier.is_active is True
        assert str(tier) == f"{creator_user.username} - Basic ($5.00/month)"

    def test_tier_max_limit(self, creator_user):
        """Test that creators can only create up to 10 tiers"""
        # Create 10 tiers
        for i in range(10):
            SubscriptionTier.objects.create(
                creator=creator_user.profile,
                name=f"Tier {i}",
                description=f"Description {i}",
                price=Decimal('5.00') * (i + 1),
                order=i
            )

        # Try to create 11th tier
        with pytest.raises(ValidationError):
            tier = SubscriptionTier(
                creator=creator_user.profile,
                name="Tier 11",
                description="Description 11",
                price=Decimal('100.00'),
                order=11
            )
            tier.save()

    def test_unique_tier_name_per_creator(self, creator_user):
        """Test that tier names must be unique per creator"""
        SubscriptionTier.objects.create(
            creator=creator_user.profile,
            name="Premium",
            description="Premium tier",
            price=Decimal('10.00')
        )

        # Try to create another tier with same name for same creator
        with pytest.raises(Exception):  # Will raise IntegrityError
            SubscriptionTier.objects.create(
                creator=creator_user.profile,
                name="Premium",
                description="Another premium tier",
                price=Decimal('15.00')
            )

    def test_subscriber_count_property(self, creator_user, regular_user):
        """Test subscriber_count property"""
        tier = SubscriptionTier.objects.create(
            creator=creator_user.profile,
            name="VIP",
            description="VIP tier",
            price=Decimal('20.00')
        )

        assert tier.subscriber_count == 0

        # Create active subscription
        TierSubscription.objects.create(
            subscriber=regular_user,
            tier=tier,
            is_active=True,
            end_date=timezone.now() + timedelta(days=30)
        )

        assert tier.subscriber_count == 1

    def test_tier_ordering(self, creator_user):
        """Test tier ordering by order and price"""
        tier1 = SubscriptionTier.objects.create(
            creator=creator_user.profile,
            name="Basic",
            price=Decimal('5.00'),
            order=2
        )
        tier2 = SubscriptionTier.objects.create(
            creator=creator_user.profile,
            name="Premium",
            price=Decimal('10.00'),
            order=1
        )
        tier3 = SubscriptionTier.objects.create(
            creator=creator_user.profile,
            name="VIP",
            price=Decimal('20.00'),
            order=0
        )

        tiers = list(SubscriptionTier.objects.filter(creator=creator_user.profile))
        assert tiers[0] == tier3  # order=0
        assert tiers[1] == tier2  # order=1
        assert tiers[2] == tier1  # order=2


@pytest.mark.django_db
class TestTierSubscriptionModel:
    """Test TierSubscription model"""

    def test_create_subscription(self, creator_user, regular_user):
        """Test creating a tier subscription"""
        tier = SubscriptionTier.objects.create(
            creator=creator_user.profile,
            name="Basic",
            description="Basic tier",
            price=Decimal('5.00')
        )

        subscription = TierSubscription.objects.create(
            subscriber=regular_user,
            tier=tier,
            is_active=True
        )

        assert subscription.subscriber == regular_user
        assert subscription.tier == tier
        assert subscription.is_active is True
        assert subscription.end_date is not None  # Auto-set to 30 days

    def test_subscription_auto_end_date(self, creator_user, regular_user):
        """Test that end_date is automatically set to 30 days"""
        tier = SubscriptionTier.objects.create(
            creator=creator_user.profile,
            name="Basic",
            description="Basic tier",
            price=Decimal('5.00')
        )

        subscription = TierSubscription.objects.create(
            subscriber=regular_user,
            tier=tier
        )

        # Check end_date is approximately 30 days from now
        expected_end = timezone.now() + timedelta(days=30)
        time_diff = abs((subscription.end_date - expected_end).total_seconds())
        assert time_diff < 5  # Within 5 seconds

    def test_cancel_subscription(self, creator_user, regular_user):
        """Test canceling a subscription"""
        tier = SubscriptionTier.objects.create(
            creator=creator_user.profile,
            name="Basic",
            description="Basic tier",
            price=Decimal('5.00')
        )

        subscription = TierSubscription.objects.create(
            subscriber=regular_user,
            tier=tier,
            is_active=True
        )

        assert subscription.cancelled_at is None
        subscription.cancel()

        assert subscription.cancelled_at is not None
        assert subscription.is_active is True  # Still active until end_date

    def test_deactivate_subscription(self, creator_user, regular_user):
        """Test immediately deactivating a subscription"""
        tier = SubscriptionTier.objects.create(
            creator=creator_user.profile,
            name="Basic",
            description="Basic tier",
            price=Decimal('5.00')
        )

        subscription = TierSubscription.objects.create(
            subscriber=regular_user,
            tier=tier,
            is_active=True
        )

        subscription.deactivate()
        assert subscription.is_active is False

    def test_is_expired_property(self, creator_user, regular_user):
        """Test is_expired property"""
        tier = SubscriptionTier.objects.create(
            creator=creator_user.profile,
            name="Basic",
            description="Basic tier",
            price=Decimal('5.00')
        )

        # Create expired subscription
        subscription = TierSubscription.objects.create(
            subscriber=regular_user,
            tier=tier,
            end_date=timezone.now() - timedelta(days=1)
        )

        assert subscription.is_expired is True

        # Create active subscription
        subscription2 = TierSubscription.objects.create(
            subscriber=regular_user,
            tier=tier,
            end_date=timezone.now() + timedelta(days=30)
        )

        assert subscription2.is_expired is False

    def test_days_remaining_property(self, creator_user, regular_user):
        """Test days_remaining property"""
        tier = SubscriptionTier.objects.create(
            creator=creator_user.profile,
            name="Basic",
            description="Basic tier",
            price=Decimal('5.00')
        )

        subscription = TierSubscription.objects.create(
            subscriber=regular_user,
            tier=tier,
            end_date=timezone.now() + timedelta(days=15)
        )

        assert subscription.days_remaining >= 14  # At least 14 days


@pytest.mark.django_db
class TestPostTierAccess:
    """Test post access with tiers"""

    def test_post_tier_assignment(self, creator_user):
        """Test assigning tiers to posts"""
        tier1 = SubscriptionTier.objects.create(
            creator=creator_user.profile,
            name="Basic",
            description="Basic tier",
            price=Decimal('5.00')
        )
        tier2 = SubscriptionTier.objects.create(
            creator=creator_user.profile,
            name="Premium",
            description="Premium tier",
            price=Decimal('10.00')
        )

        post = Post.objects.create(
            title="Test Post",
            content="Test content",
            author=creator_user,
            status='published',
            is_free=False
        )

        post.tiers.add(tier1, tier2)

        assert post.tiers.count() == 2
        assert tier1 in post.tiers.all()
        assert tier2 in post.tiers.all()

    def test_user_has_access_free_post(self, creator_user, regular_user):
        """Test that everyone has access to free posts"""
        post = Post.objects.create(
            title="Free Post",
            content="Free content",
            author=creator_user,
            status='published',
            is_free=True
        )

        assert post.user_has_access(regular_user) is True
        assert post.user_has_access(creator_user) is True

    def test_user_has_access_author(self, creator_user):
        """Test that author always has access to their posts"""
        tier = SubscriptionTier.objects.create(
            creator=creator_user.profile,
            name="Premium",
            description="Premium tier",
            price=Decimal('10.00')
        )

        post = Post.objects.create(
            title="Paid Post",
            content="Paid content",
            author=creator_user,
            status='published',
            is_free=False
        )
        post.tiers.add(tier)

        assert post.user_has_access(creator_user) is True

    def test_user_has_access_with_subscription(self, creator_user, regular_user):
        """Test that subscribed users have access to tier posts"""
        tier = SubscriptionTier.objects.create(
            creator=creator_user.profile,
            name="Premium",
            description="Premium tier",
            price=Decimal('10.00')
        )

        post = Post.objects.create(
            title="Paid Post",
            content="Paid content",
            author=creator_user,
            status='published',
            is_free=False
        )
        post.tiers.add(tier)

        # User without subscription
        assert post.user_has_access(regular_user) is False

        # Create active subscription
        TierSubscription.objects.create(
            subscriber=regular_user,
            tier=tier,
            is_active=True,
            end_date=timezone.now() + timedelta(days=30)
        )

        # User with subscription
        assert post.user_has_access(regular_user) is True

    def test_user_has_access_expired_subscription(self, creator_user, regular_user):
        """Test that expired subscriptions don't grant access"""
        tier = SubscriptionTier.objects.create(
            creator=creator_user.profile,
            name="Premium",
            description="Premium tier",
            price=Decimal('10.00')
        )

        post = Post.objects.create(
            title="Paid Post",
            content="Paid content",
            author=creator_user,
            status='published',
            is_free=False
        )
        post.tiers.add(tier)

        # Create expired subscription
        TierSubscription.objects.create(
            subscriber=regular_user,
            tier=tier,
            is_active=True,
            end_date=timezone.now() - timedelta(days=1)
        )

        assert post.user_has_access(regular_user) is False


@pytest.mark.django_db
class TestTierViews:
    """Test tier management views"""

    def test_tier_list_view_requires_login(self, client):
        """Test that tier list view requires login"""
        url = reverse('creator:tiers')
        response = client.get(url)

        assert response.status_code == 302  # Redirect to login

    def test_tier_list_view_requires_creator(self, client, regular_user):
        """Test that tier list view requires creator status"""
        client.force_login(regular_user)
        url = reverse('creator:tiers')
        response = client.get(url)

        assert response.status_code == 403  # Forbidden

    def test_tier_list_view_success(self, client, creator_user):
        """Test successful tier list view"""
        client.force_login(creator_user)

        # Create some tiers
        SubscriptionTier.objects.create(
            creator=creator_user.profile,
            name="Basic",
            description="Basic tier",
            price=Decimal('5.00')
        )
        SubscriptionTier.objects.create(
            creator=creator_user.profile,
            name="Premium",
            description="Premium tier",
            price=Decimal('10.00')
        )

        url = reverse('creator:tiers')
        response = client.get(url)

        assert response.status_code == 200
        assert b'Basic' in response.content
        assert b'Premium' in response.content

    def test_create_tier_view(self, client, creator_user):
        """Test creating a tier through view"""
        client.force_login(creator_user)
        url = reverse('creator:create_tier')

        data = {
            'name': 'VIP',
            'description': 'VIP tier with all access',
            'price': '20.00',
            'order': 0,
            'is_active': True
        }

        response = client.post(url, data)

        assert response.status_code == 302  # Redirect to tier list
        assert SubscriptionTier.objects.filter(name='VIP').exists()

    def test_edit_tier_view(self, client, creator_user):
        """Test editing a tier"""
        client.force_login(creator_user)

        tier = SubscriptionTier.objects.create(
            creator=creator_user.profile,
            name="Basic",
            description="Basic tier",
            price=Decimal('5.00')
        )

        url = reverse('creator:edit_tier', args=[tier.id])
        data = {
            'name': 'Basic Updated',
            'description': 'Updated description',
            'price': '7.50',
            'order': 0,
            'is_active': True
        }

        response = client.post(url, data)

        assert response.status_code == 302
        tier.refresh_from_db()
        assert tier.name == 'Basic Updated'
        assert tier.price == Decimal('7.50')

    def test_delete_tier_view(self, client, creator_user):
        """Test deleting a tier"""
        client.force_login(creator_user)

        tier = SubscriptionTier.objects.create(
            creator=creator_user.profile,
            name="Basic",
            description="Basic tier",
            price=Decimal('5.00')
        )

        url = reverse('creator:delete_tier', args=[tier.id])
        response = client.post(url)

        assert response.status_code == 302
        assert not SubscriptionTier.objects.filter(id=tier.id).exists()

    def test_tier_subscribers_view(self, client, creator_user, regular_user):
        """Test viewing tier subscribers"""
        client.force_login(creator_user)

        tier = SubscriptionTier.objects.create(
            creator=creator_user.profile,
            name="Premium",
            description="Premium tier",
            price=Decimal('10.00')
        )

        TierSubscription.objects.create(
            subscriber=regular_user,
            tier=tier,
            is_active=True,
            end_date=timezone.now() + timedelta(days=30)
        )

        url = reverse('creator:tier_subscribers', args=[tier.id])
        response = client.get(url)

        assert response.status_code == 200
        assert regular_user.username.encode() in response.content

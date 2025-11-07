from django.contrib.auth.models import User
from django.db import models

from .category import Category


class Post(models.Model):
    """Post model for content with draft system"""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_free = models.BooleanField(
        default=False, help_text='If True, post is visible to everyone (subscribed and unsubscribed users)'
    )
    tiers = models.ManyToManyField(
        'SubscriptionTier',
        blank=True,
        related_name='posts',
        help_text='Subscription tiers that can access this post. Leave empty if post is free.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_published(self):
        return self.status == 'published'

    @property
    def is_draft(self):
        return self.status == 'draft'

    def user_has_access(self, user):
        """Check if a user has access to this post"""
        # Author always has access
        if user == self.author:
            return True

        # Free posts are accessible to everyone
        if self.is_free:
            return True

        # If post has no tiers, treat as free
        if not self.tiers.exists():
            return True

        # Check if user has active subscription to any of the post's tiers
        if user.is_authenticated:
            from django.utils import timezone

            from .subscription import TierSubscription

            user_tier_ids = TierSubscription.objects.filter(
                subscriber=user, is_active=True, end_date__gte=timezone.now()
            ).values_list('tier_id', flat=True)

            return self.tiers.filter(id__in=user_tier_ids).exists()

        return False

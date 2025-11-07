from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from .user import UserProfile


class Subscription(models.Model):
    """Legacy subscription model - kept for backwards compatibility"""

    subscriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='subscribers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['subscriber', 'creator']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subscriber.username} follows {self.creator.user.username}"


class TierSubscription(models.Model):
    """Tier-based subscription model for paid subscriptions"""

    subscriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tier_subscriptions')
    tier = models.ForeignKey('SubscriptionTier', on_delete=models.CASCADE, related_name='subscriptions')
    is_active = models.BooleanField(default=True, help_text='Whether subscription is currently active')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(help_text='When the current subscription period ends')
    cancelled_at = models.DateTimeField(
        null=True, blank=True, help_text='When user cancelled (still active until end_date)'
    )

    # Payment tracking (placeholder for now)
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('refunded', 'Refunded'),
        ],
        default='pending',
    )
    transaction_id = models.CharField(max_length=255, blank=True, null=True, help_text='Payment transaction ID')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['subscriber', 'is_active']),
            models.Index(fields=['tier', 'is_active']),
        ]

    def __str__(self):
        return f"{self.subscriber.username} - {self.tier.name} ({'Active' if self.is_active else 'Inactive'})"

    def save(self, *args, **kwargs):
        # Set end_date to 30 days from start if not set
        if not self.end_date and not self.pk:
            self.end_date = timezone.now() + timedelta(days=30)
        super().save(*args, **kwargs)

    def cancel(self):
        """Cancel subscription - it remains active until end_date"""
        self.cancelled_at = timezone.now()
        self.save()

    def deactivate(self):
        """Immediately deactivate subscription"""
        self.is_active = False
        self.save()

    @property
    def is_expired(self):
        """Check if subscription has expired"""
        return timezone.now() > self.end_date

    @property
    def days_remaining(self):
        """Calculate days remaining in subscription"""
        if self.is_expired:
            return 0
        delta = self.end_date - timezone.now()
        return max(0, delta.days)

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from .user import UserProfile


class SubscriptionTier(models.Model):
    """Subscription tier/pricing plan created by creators"""

    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='tiers')
    name = models.CharField(max_length=100, help_text='Name of the tier (e.g., Basic, Premium, VIP)')
    description = models.TextField(max_length=1000, help_text='Description of what this tier includes')
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)], help_text='Monthly price in USD'
    )
    image = models.ImageField(upload_to='tier_images/', blank=True, null=True, help_text='Tier cover image')
    order = models.PositiveIntegerField(default=0, help_text='Display order (lower number = higher priority)')
    is_active = models.BooleanField(default=True, help_text='Whether this tier is available for subscription')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['creator', 'order', 'price']
        unique_together = ['creator', 'name']

    def __str__(self):
        return f"{self.creator.user.username} - {self.name} (${self.price}/month)"

    def clean(self):
        """Validate that creator doesn't have more than 10 tiers"""
        # Only validate if creator is set (it might not be during form validation)
        try:
            if self.creator_id:
                # Exclude current tier if updating
                existing_tiers = SubscriptionTier.objects.filter(creator_id=self.creator_id)
                if self.pk:
                    existing_tiers = existing_tiers.exclude(pk=self.pk)

                if existing_tiers.count() >= 10:
                    raise ValidationError('A creator can have a maximum of 10 subscription tiers.')
        except (AttributeError, ValueError):
            # Creator not set yet, skip validation (will be validated in form or view)
            pass

    def save(self, *args, **kwargs):
        # Only run clean if creator is set
        if self.creator_id:
            self.clean()
        super().save(*args, **kwargs)

    @property
    def subscriber_count(self):
        """Count active subscribers to this tier"""
        from .subscription import TierSubscription

        return TierSubscription.objects.filter(tier=self, is_active=True).count()

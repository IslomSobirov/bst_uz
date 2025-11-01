from django.contrib.auth.models import User
from django.db import models

from .user import UserProfile


class Subscription(models.Model):
    """Subscription model for users to follow creators"""

    subscriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='subscribers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['subscriber', 'creator']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subscriber.username} follows {self.creator.user.username}"

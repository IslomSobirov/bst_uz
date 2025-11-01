from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.db import models


class UserProfile(models.Model):
    """Extended user profile with creator capabilities"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_creator = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False, help_text='Designates whether the user can log into the admin site.')
    is_superuser = models.BooleanField(
        default=False, help_text='Designates that this user has all permissions without explicitly assigning them.'
    )
    bio = models.TextField(max_length=500, blank=True, validators=[MinLengthValidator(10)])
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s profile"

    @property
    def subscriber_count(self):
        return self.subscribers.count()

    @property
    def following_count(self):
        return self.user.following.count()

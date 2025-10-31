from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator


class UserProfile(models.Model):
    """Extended user profile with creator capabilities"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_creator = models.BooleanField(default=False)
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
        return self.following.count()


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


class Category(models.Model):
    """Category model for organizing content"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


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


class Comment(models.Model):
    """Comment model for posts"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'

from django.contrib import admin

from .models import Category, Comment, Post, Subscription, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_creator', 'subscriber_count', 'following_count', 'created_at']
    list_filter = ['is_creator', 'created_at']
    search_fields = ['user__username', 'user__email', 'bio']
    list_editable = ['is_creator']
    date_hierarchy = 'created_at'

    @admin.display(description='Subscribers')
    def subscriber_count(self, obj):
        return obj.subscriber_count

    @admin.display(description='Following')
    def following_count(self, obj):
        return obj.following_count


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['subscriber', 'creator', 'created_at']
    list_filter = ['created_at']
    search_fields = ['subscriber__username', 'creator__user__username']
    date_hierarchy = 'created_at'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'created_at']
    list_filter = ['status', 'category', 'created_at', 'author']
    search_fields = ['title', 'content', 'author__username']
    list_editable = ['status']
    date_hierarchy = 'created_at'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'author', 'content', 'created_at']
    list_filter = ['created_at', 'author']
    search_fields = ['content', 'author__username', 'post__title']
    date_hierarchy = 'created_at'

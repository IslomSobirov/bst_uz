from django.contrib import admin

from .models import Category, Comment, Post, Subscription, SubscriptionTier, TierSubscription, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'is_creator',
        'is_staff',
        'is_superuser',
        'subscriber_count',
        'following_count',
        'created_at',
    ]
    list_filter = ['is_creator', 'is_staff', 'is_superuser', 'created_at']
    search_fields = ['user__username', 'user__email', 'bio']
    list_editable = ['is_creator', 'is_staff', 'is_superuser']
    date_hierarchy = 'created_at'
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Permissions', {'fields': ('is_creator', 'is_staff', 'is_superuser')}),
        ('Profile', {'fields': ('bio', 'avatar')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ['created_at', 'updated_at']

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
    list_display = ['title', 'author', 'category', 'status', 'is_free', 'created_at']
    list_filter = ['status', 'is_free', 'category', 'created_at', 'author']
    search_fields = ['title', 'content', 'author__username']
    list_editable = ['status', 'is_free']
    filter_horizontal = ['tiers']
    date_hierarchy = 'created_at'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'author', 'content', 'created_at']
    list_filter = ['created_at', 'author']
    search_fields = ['content', 'author__username', 'post__title']
    date_hierarchy = 'created_at'


@admin.register(SubscriptionTier)
class SubscriptionTierAdmin(admin.ModelAdmin):
    list_display = ['name', 'creator', 'price', 'order', 'is_active', 'subscriber_count', 'created_at']
    list_filter = ['is_active', 'created_at', 'creator']
    search_fields = ['name', 'description', 'creator__user__username']
    list_editable = ['order', 'is_active']
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Tier Info', {'fields': ('creator', 'name', 'description', 'price')}),
        ('Display', {'fields': ('image', 'order', 'is_active')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ['created_at', 'updated_at']

    @admin.display(description='Subscribers')
    def subscriber_count(self, obj):
        return obj.subscriber_count


@admin.register(TierSubscription)
class TierSubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'subscriber',
        'tier',
        'is_active',
        'payment_status',
        'start_date',
        'end_date',
        'days_remaining',
        'cancelled_at',
    ]
    list_filter = ['is_active', 'payment_status', 'start_date', 'end_date']
    search_fields = ['subscriber__username', 'tier__name', 'transaction_id']
    date_hierarchy = 'start_date'
    fieldsets = (
        ('Subscription', {'fields': ('subscriber', 'tier', 'is_active')}),
        ('Dates', {'fields': ('start_date', 'end_date', 'cancelled_at')}),
        ('Payment', {'fields': ('payment_status', 'transaction_id')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ['created_at', 'updated_at', 'start_date']

    @admin.display(description='Days Left')
    def days_remaining(self, obj):
        return obj.days_remaining

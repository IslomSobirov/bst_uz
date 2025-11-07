from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Category, Comment, Post, Subscription, SubscriptionTier, TierSubscription, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    subscriber_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_creator',
            'bio',
            'avatar',
            'subscriber_count',
            'following_count',
            'created_at',
        ]
        read_only_fields = ['id', 'subscriber_count', 'following_count', 'created_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    is_creator = serializers.BooleanField(default=False)
    bio = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'is_creator', 'bio']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        password_confirm = validated_data.pop('password_confirm')
        is_creator = validated_data.pop('is_creator', False)
        bio = validated_data.pop('bio', '')

        user = User.objects.create_user(**validated_data)

        # Update user profile (signal already creates it, so just update it)
        profile = user.profile
        profile.is_creator = is_creator
        if bio:
            profile.bio = bio
        profile.save()

        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class SubscriptionSerializer(serializers.ModelSerializer):
    creator = UserProfileSerializer(read_only=True)
    creator_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Subscription
        fields = ['id', 'creator', 'creator_id', 'created_at']
        read_only_fields = ['id', 'created_at']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['author']

    def get_author(self, obj):
        from .serializers import UserProfileSerializer

        # Check if author is a real user (not AnonymousUser)
        if hasattr(obj.author, 'profile'):
            return UserProfileSerializer(obj.author.profile).data
        return None


class PostSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()
    is_published = serializers.BooleanField(read_only=True)
    is_draft = serializers.BooleanField(read_only=True)
    tiers = serializers.SerializerMethodField()
    user_has_access = serializers.SerializerMethodField()
    is_locked = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ['author']

    def get_author(self, obj):
        from .serializers import UserProfileSerializer

        # Check if author is a real user (not AnonymousUser)
        if hasattr(obj.author, 'profile'):
            return UserProfileSerializer(obj.author.profile).data
        return None

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_tiers(self, obj):
        """Get tier information for the post"""
        tiers = obj.tiers.all()
        return [{'id': t.id, 'name': t.name, 'price': str(t.price)} for t in tiers]

    def get_user_has_access(self, obj):
        """Check if current user has access to this post"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.user_has_access(request.user)
        return obj.is_free

    def get_is_locked(self, obj):
        """Check if post is locked for current user"""
        request = self.context.get('request')
        if obj.is_free:
            return False
        if request and hasattr(request, 'user'):
            return not obj.user_has_access(request.user)
        return True

    def get_content(self, obj):
        """Return content or locked message based on access"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if obj.user_has_access(request.user):
                return obj.content
        elif obj.is_free:
            return obj.content

        # Return preview for locked content
        preview_length = 150
        if len(obj.content) > preview_length:
            return obj.content[:preview_length] + '... [Subscribe to read more]'
        return '[This content is locked. Subscribe to view.]'


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'image', 'status', 'is_free', 'tiers']


class PostUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'image', 'status', 'is_free', 'tiers']
        read_only_fields = ['author']


class SubscriptionTierSerializer(serializers.ModelSerializer):
    creator = UserProfileSerializer(read_only=True)
    subscriber_count = serializers.IntegerField(read_only=True)
    post_count = serializers.SerializerMethodField()

    class Meta:
        model = SubscriptionTier
        fields = [
            'id',
            'creator',
            'name',
            'description',
            'price',
            'image',
            'order',
            'is_active',
            'subscriber_count',
            'post_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'subscriber_count']

    def get_post_count(self, obj):
        return obj.posts.filter(status='published').count()


class SubscriptionTierCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionTier
        fields = ['name', 'description', 'price', 'image', 'order', 'is_active']

    def validate(self, attrs):
        # Check creator's tier limit (max 10)
        request = self.context.get('request')
        if request and hasattr(request.user, 'profile'):
            creator = request.user.profile
            existing_count = SubscriptionTier.objects.filter(creator=creator).count()
            if existing_count >= 10:
                raise serializers.ValidationError('You can create a maximum of 10 subscription tiers.')
        return attrs


class TierSubscriptionSerializer(serializers.ModelSerializer):
    tier = SubscriptionTierSerializer(read_only=True)
    tier_id = serializers.IntegerField(write_only=True)
    subscriber_username = serializers.CharField(source='subscriber.username', read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = TierSubscription
        fields = [
            'id',
            'subscriber_username',
            'tier',
            'tier_id',
            'is_active',
            'start_date',
            'end_date',
            'cancelled_at',
            'payment_status',
            'transaction_id',
            'days_remaining',
            'is_expired',
            'created_at',
        ]
        read_only_fields = ['id', 'start_date', 'payment_status', 'transaction_id', 'created_at']

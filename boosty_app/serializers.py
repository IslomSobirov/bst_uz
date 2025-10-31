from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Category, Post, Comment, UserProfile, Subscription


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    subscriber_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_creator', 
                 'bio', 'avatar', 'subscriber_count', 'following_count', 'created_at']
        read_only_fields = ['id', 'subscriber_count', 'following_count', 'created_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    is_creator = serializers.BooleanField(default=False)
    bio = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 
                 'last_name', 'is_creator', 'bio']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        password_confirm = validated_data.pop('password_confirm')
        is_creator = validated_data.pop('is_creator', False)
        bio = validated_data.pop('bio', '')
        
        user = User.objects.create_user(**validated_data)
        
        # Create user profile
        UserProfile.objects.create(
            user=user,
            is_creator=is_creator,
            bio=bio
        )
        
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
        return UserProfileSerializer(obj.author.profile).data


class PostSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()
    is_published = serializers.BooleanField(read_only=True)
    is_draft = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ['author']
    
    def get_author(self, obj):
        from .serializers import UserProfileSerializer
        return UserProfileSerializer(obj.author.profile).data
    
    def get_comments_count(self, obj):
        return obj.comments.count()


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'image', 'status']


class PostUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'image', 'status']
        read_only_fields = ['author']

from django.contrib.auth import authenticate
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Comment, Post, Subscription, UserProfile
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    PostCreateSerializer,
    PostSerializer,
    PostUpdateSerializer,
    SubscriptionSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
)


class AuthViewSet(APIView):
    """Authentication views for registration and login"""

    permission_classes = [permissions.AllowAny]

    def dispatch(self, request, *args, **kwargs):
        setattr(request, '_dont_enforce_csrf_checks', True)
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, **kwargs):
        action = kwargs.get('action')
        if action == 'register':
            serializer = UserRegistrationSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                token, created = Token.objects.get_or_create(user=user)
                return Response(
                    {'token': token.key, 'user': UserProfileSerializer(user.profile).data},
                    status=status.HTTP_201_CREATED,
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif action == 'login':
            serializer = UserLoginSerializer(data=request.data)
            if serializer.is_valid():
                user = authenticate(
                    username=serializer.validated_data['username'], password=serializer.validated_data['password']
                )
                if user:
                    token, created = Token.objects.get_or_create(user=user)
                    return Response({'token': token.key, 'user': UserProfileSerializer(user.profile).data})
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for user profiles"""

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self):
        """Override to check permissions on object level"""
        obj = super().get_object()

        # Check update/delete permissions
        if self.action in ['update', 'partial_update', 'destroy']:
            if not self.request.user.is_authenticated:
                from rest_framework.exceptions import PermissionDenied

                raise PermissionDenied("Authentication required")
            if obj.user != self.request.user:
                from rest_framework.exceptions import PermissionDenied

                raise PermissionDenied("You can only modify your own profile")

        return obj

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Get current user profile"""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(request.user.profile)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def subscribe(self, request, pk=None):
        """Subscribe to a creator"""
        creator = self.get_object()
        subscriber = request.user

        if creator.user == subscriber:
            return Response({'error': 'You cannot subscribe to yourself'}, status=status.HTTP_400_BAD_REQUEST)

        subscription, created = Subscription.objects.get_or_create(subscriber=subscriber, creator=creator)

        if created:
            return Response({'status': 'Subscribed successfully'})
        else:
            return Response({'status': 'Already subscribed'})

    @action(detail=True, methods=['delete'])
    def unsubscribe(self, request, pk=None):
        """Unsubscribe from a creator"""
        creator = self.get_object()
        subscriber = request.user

        try:
            subscription = Subscription.objects.get(subscriber=subscriber, creator=creator)
            subscription.delete()
            return Response({'status': 'Unsubscribed successfully'})
        except Subscription.DoesNotExist:
            return Response({'error': 'Not subscribed'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def creators(self, request):
        """Get list of all creators, optionally filtered by category"""
        creators = UserProfile.objects.filter(is_creator=True)

        # Filter by category if provided
        category_id = request.query_params.get('category', None)
        if category_id:
            # Get creators who have published posts in this category
            creators = creators.filter(user__posts__category_id=category_id, user__posts__status='published').distinct()

        serializer = self.get_serializer(creators, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def following(self, request):
        """Get creators that the current user follows"""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        following = UserProfile.objects.filter(subscribers__subscriber=request.user)
        serializer = self.get_serializer(following, many=True)
        return Response(serializer.data)


class SubscriptionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing subscriptions"""

    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        creator = get_object_or_404(UserProfile, id=serializer.validated_data['creator_id'])
        # Check if subscription already exists
        if Subscription.objects.filter(subscriber=self.request.user, creator=creator).exists():
            from rest_framework.exceptions import ValidationError

            raise ValidationError({'creator_id': 'Already subscribed to this creator'})
        serializer.save(subscriber=self.request.user, creator=creator)

    def get_queryset(self):
        """Filter subscriptions to only show current user's subscriptions"""
        return Subscription.objects.filter(subscriber=self.request.user)

    def get_object(self):
        """Override to check permissions"""
        obj = super().get_object()
        if obj.subscriber != self.request.user:
            from rest_framework.exceptions import NotFound

            raise NotFound("Subscription not found")
        return obj


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for categories"""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class PostViewSet(viewsets.ModelViewSet):
    """ViewSet for posts with enhanced functionality"""

    queryset = Post.objects.all()  # Default queryset for router
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Filter posts - show free posts to everyone, paid posts only to subscribers"""
        if self.action == 'list':
            # Show published posts
            # - Free posts: visible to everyone
            # - Paid posts: only visible to subscribers
            if self.request.user.is_authenticated:
                # Get creators the user is subscribed to
                subscribed_creators = UserProfile.objects.filter(subscribers__subscriber=self.request.user)
                subscribed_author_ids = [creator.user.id for creator in subscribed_creators]

                # Show free published posts OR paid posts from subscribed creators
                return Post.objects.filter(
                    Q(status='published', is_free=True)
                    | Q(status='published', is_free=False, author_id__in=subscribed_author_ids)
                ).distinct()
            else:
                # Unauthenticated users can only see free published posts
                return Post.objects.filter(status='published', is_free=True)
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            # Allow access to own posts (any status) or published posts user can access
            if self.request.user.is_authenticated:
                subscribed_creators = UserProfile.objects.filter(subscribers__subscriber=self.request.user)
                subscribed_author_ids = [creator.user.id for creator in subscribed_creators]

                return Post.objects.filter(
                    Q(author=self.request.user)
                    | Q(status='published', is_free=True)
                    | Q(status='published', is_free=False, author_id__in=subscribed_author_ids)
                ).distinct()
            else:
                # Unauthenticated users can only access free published posts
                return Post.objects.filter(status='published', is_free=True)
        return Post.objects.all()

    def get_object(self):
        """Override to check permissions on object level"""
        obj = super().get_object()

        # Check update/delete permissions
        if self.action in ['update', 'partial_update', 'destroy']:
            if not self.request.user.is_authenticated:
                from rest_framework.exceptions import PermissionDenied

                raise PermissionDenied("Authentication required")
            if obj.author != self.request.user:
                from rest_framework.exceptions import PermissionDenied

                raise PermissionDenied("You can only modify your own posts")

        return obj

    def get_serializer_class(self):
        if self.action == 'create':
            return PostCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PostUpdateSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish a draft post"""
        post = self.get_object()
        if post.author == request.user and post.status == 'draft':
            post.status = 'published'
            post.save()
            return Response({'status': 'post published'})
        return Response({'error': 'You can only publish your own draft posts'}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive a published post"""
        post = self.get_object()
        if post.author == request.user and post.status == 'published':
            post.status = 'archived'
            post.save()
            return Response({'status': 'post archived'})
        return Response({'error': 'You can only archive your own published posts'}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_posts(self, request):
        """Get current user's posts (all statuses)"""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        posts = Post.objects.filter(author=request.user)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def feed(self, request):
        """Get feed of posts from subscribed creators"""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        # Get posts from creators the user follows
        following_creators = UserProfile.objects.filter(subscribers__subscriber=request.user)
        posts = Post.objects.filter(author__profile__in=following_creators, status='published').order_by('-created_at')

        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """Get comments for a specific post"""
        post = self.get_object()
        comments = post.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for comments"""

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Filter comments - show comments on free posts to everyone, paid posts only to subscribers"""
        # Comments on free published posts are visible to everyone
        # Comments on paid published posts are only visible to subscribers
        # Comments on own posts (any status) are visible to authenticated users
        if self.request.user.is_authenticated:
            # Get creators the user is subscribed to
            subscribed_creators = UserProfile.objects.filter(subscribers__subscriber=self.request.user)
            subscribed_author_ids = [creator.user.id for creator in subscribed_creators]

            # Comments on free published posts OR paid posts from subscribed creators OR own posts
            return Comment.objects.filter(
                Q(post__status='published', post__is_free=True)
                | Q(post__status='published', post__is_free=False, post__author_id__in=subscribed_author_ids)
                | Q(post__author=self.request.user)
            ).distinct()
        else:
            # Unauthenticated users can only see comments on free published posts
            return Comment.objects.filter(post__status='published', post__is_free=True)

    def perform_create(self, serializer):
        # Check if user can access the post before creating comment
        # All comments require authentication
        if not self.request.user.is_authenticated:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("You must be logged in to comment")

        post = serializer.validated_data.get('post')
        if post:
            # Users can always comment on their own posts
            if post.author == self.request.user:
                serializer.save(author=self.request.user)
                return

            # Check if post is accessible for authenticated users
            # Authenticated users can comment on free posts or paid posts if they're subscribed
            subscribed_creators = UserProfile.objects.filter(subscribers__subscriber=self.request.user)
            subscribed_author_ids = [creator.user.id for creator in subscribed_creators]

            # Allow if free published post OR paid published post with subscription
            if not (post.status == 'published' and (post.is_free or post.author_id in subscribed_author_ids)):
                from rest_framework.exceptions import PermissionDenied

                raise PermissionDenied("You must be a subscriber to comment on this post")

        serializer.save(author=self.request.user)

    def get_object(self):
        """Override to check permissions on object level"""
        obj = super().get_object()

        # Check update/delete permissions
        if self.action in ['update', 'partial_update', 'destroy']:
            if not self.request.user.is_authenticated:
                from rest_framework.exceptions import PermissionDenied

                raise PermissionDenied("Authentication required")
            if obj.author != self.request.user:
                from rest_framework.exceptions import PermissionDenied

                raise PermissionDenied("You can only modify your own comments")

        return obj

    def update(self, request, *args, **kwargs):
        """Override update to check permissions"""
        obj = self.get_object()
        if obj.author != request.user:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("You can only modify your own comments")
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """Override partial_update to check permissions"""
        obj = self.get_object()
        if obj.author != request.user:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("You can only modify your own comments")
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Override destroy to check permissions"""
        obj = self.get_object()
        if obj.author != request.user:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("You can only modify your own comments")
        return super().destroy(request, *args, **kwargs)

from django.contrib.auth import authenticate
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Comment, Post, Subscription, SubscriptionTier, TierSubscription, UserProfile
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    PostCreateSerializer,
    PostSerializer,
    PostUpdateSerializer,
    SubscriptionSerializer,
    SubscriptionTierCreateSerializer,
    SubscriptionTierSerializer,
    TierSubscriptionSerializer,
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

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def tiers(self, request, pk=None):
        """Get a creator's subscription tiers"""
        creator = self.get_object()
        if not creator.is_creator:
            return Response({'error': 'This user is not a creator'}, status=status.HTTP_400_BAD_REQUEST)
        tiers = SubscriptionTier.objects.filter(creator=creator, is_active=True).order_by('order', 'price')
        serializer = SubscriptionTierSerializer(tiers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def posts(self, request, pk=None):
        """Get a creator's posts (free + locked paid posts for non-subscribers)"""
        creator = self.get_object()
        posts = Post.objects.filter(author=creator.user, status='published').order_by('-created_at')
        serializer = PostSerializer(posts, many=True, context={'request': request})
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
        """Filter posts - show free posts and locked/unlocked paid posts"""
        from django.utils import timezone

        if self.action == 'list':
            # Show all published posts, but locked status will be determined in serializer
            return Post.objects.filter(status='published').distinct()
        elif self.action == 'retrieve':
            # For retrieve, show published posts or own posts
            if self.request.user.is_authenticated:
                return Post.objects.filter(Q(status='published') | Q(author=self.request.user)).distinct()
            else:
                return Post.objects.filter(status='published')
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Only show own posts for modification
            if self.request.user.is_authenticated:
                return Post.objects.filter(author=self.request.user)
            return Post.objects.none()
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


class SubscriptionTierViewSet(viewsets.ModelViewSet):
    """ViewSet for managing subscription tiers"""

    queryset = SubscriptionTier.objects.filter(is_active=True)
    serializer_class = SubscriptionTierSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Filter tiers based on action"""
        if self.action == 'list':
            # For list, filter by creator if provided
            creator_id = self.request.query_params.get('creator_id', None)
            if creator_id:
                return SubscriptionTier.objects.filter(creator_id=creator_id, is_active=True).order_by('order', 'price')
            return SubscriptionTier.objects.filter(is_active=True).order_by('order', 'price')
        elif self.action in ['update', 'partial_update', 'destroy']:
            # For modifications, only show user's own tiers
            if self.request.user.is_authenticated and hasattr(self.request.user, 'profile'):
                return SubscriptionTier.objects.filter(creator=self.request.user.profile)
            return SubscriptionTier.objects.none()
        return SubscriptionTier.objects.filter(is_active=True)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SubscriptionTierCreateSerializer
        return SubscriptionTierSerializer

    def perform_create(self, serializer):
        """Create tier for current user's profile"""
        if not self.request.user.profile.is_creator:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Only creators can create subscription tiers")
        serializer.save(creator=self.request.user.profile)

    def get_object(self):
        """Override to check permissions"""
        obj = super().get_object()
        if self.action in ['update', 'partial_update', 'destroy']:
            if not self.request.user.is_authenticated:
                from rest_framework.exceptions import PermissionDenied

                raise PermissionDenied("Authentication required")
            if obj.creator != self.request.user.profile:
                from rest_framework.exceptions import PermissionDenied

                raise PermissionDenied("You can only modify your own tiers")
        return obj

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_tiers(self, request):
        """Get current user's tiers"""
        if not request.user.profile.is_creator:
            return Response({'error': 'Only creators can have tiers'}, status=status.HTTP_403_FORBIDDEN)
        tiers = SubscriptionTier.objects.filter(creator=request.user.profile).order_by('order', 'price')
        serializer = self.get_serializer(tiers, many=True)
        return Response(serializer.data)


class TierSubscriptionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing tier subscriptions (user subscriptions to tiers)"""

    queryset = TierSubscription.objects.all()
    serializer_class = TierSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Only show user's own subscriptions"""
        return TierSubscription.objects.filter(subscriber=self.request.user)

    def perform_create(self, serializer):
        """Create a new tier subscription (placeholder payment)"""
        tier = get_object_or_404(SubscriptionTier, id=serializer.validated_data['tier_id'])

        # Check if tier is active
        if not tier.is_active:
            from rest_framework.exceptions import ValidationError

            raise ValidationError({'tier_id': 'This tier is not available for subscription'})

        # Check if already subscribed to this tier
        existing = TierSubscription.objects.filter(subscriber=self.request.user, tier=tier, is_active=True).first()
        if existing:
            from rest_framework.exceptions import ValidationError

            raise ValidationError({'tier_id': 'You are already subscribed to this tier'})

        # Create subscription (with placeholder payment)
        from datetime import timedelta

        from django.utils import timezone

        serializer.save(
            subscriber=self.request.user,
            tier=tier,
            is_active=True,
            payment_status='completed',  # Placeholder - assume payment successful
            transaction_id=f'PLACEHOLDER_{self.request.user.id}_{tier.id}_{timezone.now().timestamp()}',
        )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a tier subscription"""
        subscription = self.get_object()
        if subscription.cancelled_at:
            return Response({'error': 'Subscription already cancelled'}, status=status.HTTP_400_BAD_REQUEST)

        subscription.cancel()
        return Response(
            {
                'status': 'Subscription cancelled',
                'message': f'Your subscription will remain active until {subscription.end_date.strftime("%Y-%m-%d")}',
            }
        )

    @action(detail=False, methods=['get'])
    def my_subscriptions(self, request):
        """Get current user's active tier subscriptions"""
        subscriptions = TierSubscription.objects.filter(subscriber=request.user, is_active=True)
        serializer = self.get_serializer(subscriptions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_creator(self, request):
        """Get user's subscriptions grouped by creator"""
        creator_id = request.query_params.get('creator_id')
        if not creator_id:
            return Response({'error': 'creator_id parameter required'}, status=status.HTTP_400_BAD_REQUEST)

        subscriptions = TierSubscription.objects.filter(
            subscriber=request.user, tier__creator_id=creator_id, is_active=True
        )
        serializer = self.get_serializer(subscriptions, many=True)
        return Response(serializer.data)

"""Creator dashboard views for managing posts, comments, and subscribers"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import activate
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods

from .forms import PostForm
from .models import Category, Comment, Post, Subscription, UserProfile


def activate_ru(view_func):
    """Decorator to activate Russian language for views"""

    def wrapper(request, *args, **kwargs):
        activate('ru')
        return view_func(request, *args, **kwargs)

    return wrapper


def creator_required(view_func):
    """Decorator to ensure user is a creator"""

    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login

            # Redirect to admin login, then back to the creator dashboard
            return redirect_to_login(request.get_full_path(), login_url='/admin/login/')

        # Get profile (should exist due to signal, but handle edge case)
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            # If profile doesn't exist for some reason, create it
            profile = UserProfile.objects.create(user=request.user)

        if not profile.is_creator:
            # Return a friendly error page instead of raising PermissionDenied
            from django.contrib import messages

            messages.error(
                request,
                _(
                    "You must be a creator to access this page. Please update your profile in Django Admin to enable creator mode."
                ),
            )
            return render(
                request,
                'creator/not_creator.html',
                {
                    'user': request.user,
                    'profile': profile,
                },
                status=403,
            )

        return view_func(request, *args, **kwargs)

    return wrapper


@login_required
@creator_required
@activate_ru
def creator_dashboard(request):
    """Main creator dashboard showing overview statistics"""
    profile = request.user.profile

    # Get statistics
    posts = Post.objects.filter(author=request.user)
    total_posts = posts.count()
    published_posts = posts.filter(status='published').count()
    draft_posts = posts.filter(status='draft').count()
    archived_posts = posts.filter(status='archived').count()

    # Get recent posts
    recent_posts = posts[:5]

    # Get recent comments
    recent_comments = Comment.objects.filter(post__author=request.user).order_by('-created_at')[:5]

    # Get subscriber count
    subscriber_count = profile.subscriber_count

    # Get recent subscribers
    recent_subscriptions = Subscription.objects.filter(creator=profile).order_by('-created_at')[:5]

    context = {
        'profile': profile,
        'total_posts': total_posts,
        'published_posts': published_posts,
        'draft_posts': draft_posts,
        'archived_posts': archived_posts,
        'subscriber_count': subscriber_count,
        'recent_posts': recent_posts,
        'recent_comments': recent_comments,
        'recent_subscriptions': recent_subscriptions,
    }

    return render(request, 'creator/dashboard.html', context)


@login_required
@creator_required
@activate_ru
def creator_posts(request):
    """List all posts created by the creator"""
    status_filter = request.GET.get('status', 'all')

    posts = Post.objects.filter(author=request.user)

    if status_filter != 'all':
        posts = posts.filter(status=status_filter)

    posts = posts.order_by('-created_at')

    context = {
        'posts': posts,
        'status_filter': status_filter,
    }

    return render(request, 'creator/posts.html', context)


@login_required
@creator_required
@activate_ru
def create_post(request):
    """Create a new post"""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('creator:posts')
    else:
        form = PostForm()

    context = {
        'form': form,
        'action': _('Create'),
    }

    return render(request, 'creator/post_form.html', context)


@login_required
@creator_required
@activate_ru
def edit_post(request, post_id):
    """Edit an existing post"""
    post = get_object_or_404(Post, id=post_id, author=request.user)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('creator:posts')
    else:
        form = PostForm(instance=post)

    context = {
        'form': form,
        'post': post,
        'action': _('Edit'),
    }

    return render(request, 'creator/post_form.html', context)


@login_required
@creator_required
@require_http_methods(["POST"])
def delete_post(request, post_id):
    """Delete a post"""
    post = get_object_or_404(Post, id=post_id, author=request.user)
    post.delete()
    return redirect('creator:posts')


@login_required
@creator_required
@activate_ru
def creator_comments(request):
    """Review comments on creator's posts"""
    # Get all comments on posts by this creator
    comments = (
        Comment.objects.filter(post__author=request.user).select_related('post', 'author').order_by('-created_at')
    )

    # Filter by post if specified
    post_id = request.GET.get('post')
    if post_id:
        comments = comments.filter(post_id=post_id)

    context = {
        'comments': comments,
        'selected_post_id': post_id,
    }

    return render(request, 'creator/comments.html', context)


@login_required
@creator_required
@activate_ru
def view_post(request, post_id):
    """View a post detail with all comments"""
    post = get_object_or_404(Post, id=post_id, author=request.user)
    comments = Comment.objects.filter(post=post).select_related('author').order_by('created_at')

    context = {
        'post': post,
        'comments': comments,
    }

    return render(request, 'creator/post_detail.html', context)


@login_required
@creator_required
@activate_ru
def creator_subscribers(request):
    """View all subscribers"""
    profile = request.user.profile
    subscriptions = Subscription.objects.filter(creator=profile).select_related('subscriber').order_by('-created_at')

    context = {
        'subscriptions': subscriptions,
        'subscriber_count': len(subscriptions),
    }

    return render(request, 'creator/subscribers.html', context)

"""URL configuration for creator dashboard"""

from django.urls import path

from . import creator_views

app_name = 'creator'

urlpatterns = [
    path('', creator_views.creator_dashboard, name='dashboard'),
    path('posts/', creator_views.creator_posts, name='posts'),
    path('posts/create/', creator_views.create_post, name='create_post'),
    path('posts/<int:post_id>/', creator_views.view_post, name='view_post'),
    path('posts/<int:post_id>/edit/', creator_views.edit_post, name='edit_post'),
    path('posts/<int:post_id>/delete/', creator_views.delete_post, name='delete_post'),
    path('comments/', creator_views.creator_comments, name='comments'),
    path('subscribers/', creator_views.creator_subscribers, name='subscribers'),
]

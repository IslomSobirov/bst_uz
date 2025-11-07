from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'profiles', views.UserProfileViewSet)
router.register(r'subscriptions', views.SubscriptionViewSet)
router.register(r'tiers', views.SubscriptionTierViewSet, basename='tier')
router.register(r'tier-subscriptions', views.TierSubscriptionViewSet, basename='tier-subscription')
router.register(r'categories', views.CategoryViewSet)
router.register(r'posts', views.PostViewSet, basename='post')
router.register(r'comments', views.CommentViewSet)

app_name = 'boosty_app'


# Create a csrf_exempt wrapper for DRF auth URLs
@csrf_exempt
def csrf_exempt_auth(request, *args, **kwargs):
    from rest_framework.views import obtain_auth_token

    return obtain_auth_token(request, *args, **kwargs)


urlpatterns = [
    path('', include(router.urls)),
    # Custom auth endpoints (CSRF exempt)
    path('auth/register/', csrf_exempt(views.AuthViewSet.as_view()), {'action': 'register'}, name='auth-register'),
    path('auth/login/', csrf_exempt(views.AuthViewSet.as_view()), {'action': 'login'}, name='auth-login'),
    path('auth/token/', csrf_exempt_auth, name='obtain-auth-token'),
]
